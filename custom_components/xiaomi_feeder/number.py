"""Number platform for Xiaomi Smart Pet Feeder 2."""
from __future__ import annotations

from typing import Optional

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTime
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
    """Set up Xiaomi Feeder numbers."""
    coordinator: XiaomiFeederCoordinator = hass.data[DOMAIN][entry.entry_id]

    numbers: list[NumberEntity] = [
        XiaomiFeederManualPortionsNumber(coordinator, entry),
        XiaomiFeederTargetPortionsNumber(coordinator, entry),
        XiaomiFeederDesiccantLifespanNumber(coordinator, entry),
        XiaomiFeederRefillIntervalNumber(coordinator, entry),
        XiaomiFeederIntakeThresholdNumber(coordinator, entry),
    ]

    async_add_entities(numbers)


class XiaomiFeederBaseNumber(CoordinatorEntity[XiaomiFeederCoordinator], NumberEntity):
    """Base class for Xiaomi Feeder number entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        """Initialize base number."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=coordinator.device_name,
            manufacturer="Xiaomi",
            model=DEFAULT_MODEL,
        )


class XiaomiFeederManualPortionsNumber(XiaomiFeederBaseNumber):
    """Manual dispense portions slider."""

    _attr_translation_key = "manual_portions"
    _attr_native_min_value = 1
    _attr_native_max_value = 30
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:counter"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_manual_portions"
        self._attr_name = "Manual Feed Portions"

    @property
    def native_value(self) -> float:
        return float(self.coordinator.manual_portions)

    async def async_set_native_value(self, value: float) -> None:
        self.coordinator.manual_portions = int(value)
        self.async_write_ha_state()


class XiaomiFeederTargetPortionsNumber(XiaomiFeederBaseNumber):
    """RAM default feeding portions setting."""

    _attr_translation_key = "target_portions"
    _attr_native_min_value = 1
    _attr_native_max_value = 30
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:numeric"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_target_portions"
        self._attr_name = "Target Feeding Portions"

    @property
    def native_value(self) -> Optional[float]:
        if self.coordinator.data and self.coordinator.data.status:
            val = self.coordinator.data.status.target_feeding_portions
            return float(val) if val is not None else None
        return None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_target_portions(int(value))


class XiaomiFeederDesiccantLifespanNumber(XiaomiFeederBaseNumber):
    """Desiccant replacement duration setting."""

    _attr_translation_key = "desiccant_lifespan"
    _attr_native_min_value = 1
    _attr_native_max_value = 180
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.DAYS
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:calendar-range"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_desiccant_lifespan"
        self._attr_name = "Desiccant Lifespan (Days)"

    @property
    def native_value(self) -> float:
        if self.coordinator.data:
            return float(self.coordinator.data.desiccant_lifespan)
        return 30.0

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_desiccant_lifespan(int(value))


class XiaomiFeederRefillIntervalNumber(XiaomiFeederBaseNumber):
    """Hopper refill reminder interval cycle."""

    _attr_translation_key = "refill_interval"
    _attr_native_min_value = 1
    _attr_native_max_value = 24
    _attr_native_step = 1
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:timer-sand"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_refill_interval"
        self._attr_name = "Refill Reminder Interval"

    @property
    def native_value(self) -> Optional[float]:
        if self.coordinator.data and self.coordinator.data.status:
            val = self.coordinator.data.status.refill_reminder_hours
            return float(val) if val is not None else 6.0
        return 6.0

    async def async_set_native_value(self, value: float) -> None:
        enabled = True
        if self.coordinator.data and self.coordinator.data.status:
            enabled = bool(self.coordinator.data.status.refill_reminder_enabled)
        await self.coordinator.async_set_refill_reminder(enabled, int(value))


class XiaomiFeederIntakeThresholdNumber(XiaomiFeederBaseNumber):
    """Low food intake threshold percentage."""

    _attr_translation_key = "intake_threshold"
    _attr_native_min_value = 1
    _attr_native_max_value = 100
    _attr_native_step = 1
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.BOX
    _attr_icon = "mdi:percent"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_intake_threshold"
        self._attr_name = "Low Intake Alarm Threshold"

    @property
    def native_value(self) -> Optional[float]:
        if self.coordinator.data and self.coordinator.data.status:
            val = self.coordinator.data.status.intake_alarm_threshold
            return float(val) if val is not None else 10.0
        return 10.0

    async def async_set_native_value(self, value: float) -> None:
        enabled = True
        if self.coordinator.data and self.coordinator.data.status:
            enabled = bool(self.coordinator.data.status.intake_alarm_enabled)
        await self.coordinator.async_set_intake_alarm(enabled, int(value))
