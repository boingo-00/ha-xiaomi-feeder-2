"""Text platform for Xiaomi Smart Pet Feeder 2."""
from __future__ import annotations

from typing import Optional

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_MODEL, DOMAIN
from .coordinator import XiaomiFeederCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Xiaomi Feeder text entities."""
    coordinator: XiaomiFeederCoordinator = hass.data[DOMAIN][entry.entry_id]

    text_entities: list[TextEntity] = [
        XiaomiFeederScheduleText(coordinator, entry),
    ]

    async_add_entities(text_entities)


class XiaomiFeederScheduleText(CoordinatorEntity[XiaomiFeederCoordinator], TextEntity):
    """Hardware schedule hex string entity for direct compatibility with dispenser-schedule-card."""

    _attr_has_entity_name = True
    _attr_translation_key = "hardware_schedule"
    _attr_native_min = 0
    _attr_native_max = 280
    _attr_icon = "mdi:calendar-edit"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_hardware_schedule"
        self._attr_name = "Hardware Schedule"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=coordinator.device_name,
            manufacturer="Xiaomi",
            model=DEFAULT_MODEL,
        )

    @property
    def native_value(self) -> Optional[str]:
        if self.coordinator.data and self.coordinator.data.schedule:
            return self.coordinator.data.schedule.raw_string
        return ""

    async def async_set_value(self, value: str) -> None:
        """Write new schedule string directly into device hardware EEPROM."""
        await self.coordinator.async_write_hardware_schedule(value)
