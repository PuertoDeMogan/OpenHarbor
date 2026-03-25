from __future__ import annotations
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_SUBMISSION_ENDPOINT, ATTR_WRITABLE, DOMAIN
from .coordinator import OpenHarborCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators: dict[str, OpenHarborCoordinator] = hass.data[DOMAIN][entry.entry_id]

    for port_id, coordinator in coordinators.items():
        known_keys: set[str] = set()

        def _add_new_sensors(_coordinator=coordinator, _port_id=port_id) -> None:
            new_entities = []
            for key, meta in _coordinator.data.get("sensors", {}).items():
                if key not in known_keys:
                    known_keys.add(key)
                    new_entities.append(OpenHarborSensor(_coordinator, _port_id, key, meta))
            if new_entities:
                async_add_entities(new_entities)

        _add_new_sensors()
        coordinator.async_add_listener(_add_new_sensors)


class OpenHarborSensor(CoordinatorEntity[OpenHarborCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: OpenHarborCoordinator,
        port_id: str,
        sensor_key: str,
        sensor_meta: dict[str, Any],
    ) -> None:
        super().__init__(coordinator)
        self._port_id = port_id
        self._sensor_key = sensor_key
        self._attr_unique_id = f"{DOMAIN}_{port_id}_{sensor_key}"
        self._attr_name = sensor_key.replace("_", " ").title()
        self._attr_icon = sensor_meta.get("icon")
        raw_unit = sensor_meta.get("unit")
        self._attr_native_unit_of_measurement = None if raw_unit == "ud" else raw_unit

        value = sensor_meta.get("value")
        self._attr_state_class = (
            SensorStateClass.MEASUREMENT if isinstance(value, (int, float)) else None
        )

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, port_id)},
            name=coordinator.data.get("name", port_id),
            manufacturer="Open Harbor",
            model="Monitor de Puerto Maritimo",
        )

    @property
    def native_value(self) -> Any:
        return (
            self.coordinator.data
            .get("sensors", {})
            .get(self._sensor_key, {})
            .get("value")
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        sensor = self.coordinator.data.get("sensors", {}).get(self._sensor_key, {})
        attrs = {
            ATTR_WRITABLE: sensor.get("writable", False),
            ATTR_SUBMISSION_ENDPOINT: self.coordinator.data.get("submission_endpoint"),
        }
        for key in ("type", "options", "min", "max"):
            if key in sensor:
                attrs[key] = sensor[key]
        return attrs
