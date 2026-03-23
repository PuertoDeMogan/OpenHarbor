"""Open Harbor integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_PORT_IDS, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import OpenHarborCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Open Harbor from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Options flow tiene prioridad sobre data (permite reconfiguración)
    config = {**entry.data, **entry.options}

    port_ids: list[str] = config[CONF_PORT_IDS]
    scan_interval: int = config.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    coordinators: dict[str, OpenHarborCoordinator] = {}

    for port_id in port_ids:
        coordinator = OpenHarborCoordinator(hass, port_id, scan_interval)
        await coordinator.async_config_entry_first_refresh()
        coordinators[port_id] = coordinator

    hass.data[DOMAIN][entry.entry_id] = coordinators

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Listener para recargar si cambian las opciones
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
