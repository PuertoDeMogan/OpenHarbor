from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DATA_REPO_BASE_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class OpenHarborCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, port_id: str, scan_interval: int) -> None:
        self.port_id = port_id
        self._url = f"{DATA_REPO_BASE_URL}/{port_id}.json"

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{port_id}",
            update_interval=timedelta(minutes=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(
                self._url, timeout=aiohttp.ClientTimeout(total=15)
            ) as resp:
                resp.raise_for_status()
                return await resp.json(content_type=None)
        except aiohttp.ClientResponseError as err:
            raise UpdateFailed(f"HTTP error {err.status} fetching {self._url}") from err
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Connection error fetching {self._url}") from err
