from __future__ import annotations

import aiohttp

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import OpenHarborCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators: dict[str, OpenHarborCoordinator] = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for port_id, coordinator in coordinators.items():
        for cam in coordinator.data.get("cameras", []):
            entities.append(OpenHarborCamera(coordinator, port_id, cam))

    async_add_entities(entities)


class OpenHarborCamera(Camera):
    _attr_has_entity_name = True
    _attr_supported_features = CameraEntityFeature.STREAM

    def __init__(
        self,
        coordinator: OpenHarborCoordinator,
        port_id: str,
        cam: dict,
    ) -> None:
        super().__init__()
        self._coordinator = coordinator
        self._port_id = port_id
        self._cam = cam
        self._attr_unique_id = f"{DOMAIN}_{port_id}_camera_{cam['id']}"
        self._attr_name = cam.get("name", cam["id"])
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, port_id)},
            name=coordinator.data.get("name", port_id),
            manufacturer="Open Harbor",
            model="Monitor de Puerto Maritimo",
        )

    async def stream_source(self) -> str | None:
        return self._cam.get("stream_url")

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        still_url = self._cam.get("still_image_url")
        if not still_url:
            return None
        session = async_get_clientsession(self.hass)
        try:
            async with session.get(
                still_url, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                resp.raise_for_status()
                return await resp.read()
        except Exception:
            return None

    @property
    def is_streaming(self) -> bool:
        return bool(self._cam.get("stream_url"))

    @property
    def use_stream_for_stills(self) -> bool:
        return bool(self._cam.get("stream_url"))
