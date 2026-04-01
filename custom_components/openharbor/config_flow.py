from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_PORT_IDS,
    CONF_SCAN_INTERVAL,
    DATA_REPO_BASE_URL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    PORTS_INDEX_URL,
)

_LOGGER = logging.getLogger(__name__)


async def _fetch_available_ports(session: aiohttp.ClientSession) -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json"}

    async with session.get(
        PORTS_INDEX_URL,
        headers=headers,
        timeout=aiohttp.ClientTimeout(total=10),
    ) as resp:
        resp.raise_for_status()
        files: list[dict] = await resp.json(content_type=None)

    port_files = [
        f for f in files
        if f.get("type") == "file" and f["name"].endswith(".json")
    ]

    async def _fetch_port_name(file_entry: dict) -> tuple[str, str]:
        port_id = file_entry["name"].removesuffix(".json")
        try:
            async with session.get(
                file_entry["download_url"],
                timeout=aiohttp.ClientTimeout(total=10),
            ) as r:
                r.raise_for_status()
                data = await r.json(content_type=None)
                name = data.get("name", port_id.replace("_", " ").title())
        except Exception:
            _LOGGER.warning("Could not fetch name for port %s, using fallback", port_id)
            name = port_id.replace("_", " ").title()
        return port_id, name

    results = await asyncio.gather(*[_fetch_port_name(f) for f in port_files])
    return dict(results)


def _build_schema(
    available_ports: dict[str, str],
    default_ports: list[str] | None = None,
    default_interval: int = DEFAULT_SCAN_INTERVAL,
) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_PORT_IDS, default=default_ports or []): SelectSelector(
                SelectSelectorConfig(
                    options=[
                        {"value": pid, "label": name}
                        for pid, name in available_ports.items()
                    ],
                    multiple=True,
                    mode=SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Optional(CONF_SCAN_INTERVAL, default=default_interval): NumberSelector(
                NumberSelectorConfig(
                    min=MIN_SCAN_INTERVAL,
                    max=MAX_SCAN_INTERVAL,
                    step=30,
                    mode=NumberSelectorMode.BOX,
                    unit_of_measurement="min",
                )
            ),
        }
    )


class OpenHarborConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._available_ports: dict[str, str] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if not self._available_ports:
            try:
                session = async_get_clientsession(self.hass)
                self._available_ports = await _fetch_available_ports(session)
            except aiohttp.ClientResponseError:
                errors["base"] = "cannot_connect"
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error fetching port list")
                errors["base"] = "unknown"

        if not errors and user_input is not None:
            selected_ids: list[str] = user_input[CONF_PORT_IDS]

            if not selected_ids:
                errors[CONF_PORT_IDS] = "no_ports_selected"
            else:
                await self.async_set_unique_id("_".join(sorted(selected_ids)))
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=self._build_title(selected_ids),
                    data={
                        CONF_PORT_IDS: selected_ids,
                        CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL]),
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema(self._available_ports),
            errors=errors,
        )

    def _build_title(self, port_ids: list[str]) -> str:
        names = [self._available_ports.get(pid, pid) for pid in port_ids]
        if len(names) == 1:
            return names[0]
        return f"{names[0]} +{len(names) - 1}"

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return OpenHarborOptionsFlow(config_entry)


class OpenHarborOptionsFlow(OptionsFlow):
    def __init__(self, config_entry: ConfigEntry) -> None:
        self._config_entry = config_entry
        self._available_ports: dict[str, str] = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if not self._available_ports:
            try:
                session = async_get_clientsession(self.hass)
                self._available_ports = await _fetch_available_ports(session)
            except aiohttp.ClientError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error fetching port list")
                errors["base"] = "unknown"

        if not errors and user_input is not None:
            if not user_input[CONF_PORT_IDS]:
                errors[CONF_PORT_IDS] = "no_ports_selected"
            else:
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_PORT_IDS: user_input[CONF_PORT_IDS],
                        CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL]),
                    },
                )

        current = {**self._config_entry.data, **self._config_entry.options}

        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(
                self._available_ports,
                default_ports=current.get(CONF_PORT_IDS, []),
                default_interval=current.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ),
            errors=errors,
        )
