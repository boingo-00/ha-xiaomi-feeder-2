"""Switch platform for Xiaomi Smart Pet Feeder 2."""
from __future__ import annotations

from typing import Any, Optional

from homeassistant.components.switch import SwitchEntity
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
    """Set up Xiaomi Feeder switches."""
    coordinator: XiaomiFeederCoordinator = hass.data[DOMAIN][entry.entry_id]

    switches: list[SwitchEntity] = [
        XiaomiFeederScreenSleepSwitch(coordinator, entry),
        XiaomiFeederScreenProgressSwitch(coordinator, entry),
        XiaomiFeederChildLockSwitch(coordinator, entry),
        XiaomiFeederAntiStackingSwitch(coordinator, entry),
        XiaomiFeederGrainCompensationSwitch(coordinator, entry),
        XiaomiFeederScheduleEnabledSwitch(coordinator, entry),
        XiaomiFeederSkipNextMealSwitch(coordinator, entry),
        XiaomiFeederRefillReminderSwitch(coordinator, entry),
        XiaomiFeederIntakeAlarmSwitch(coordinator, entry),
    ]

    async_add_entities(switches)


class XiaomiFeederBaseSwitch(CoordinatorEntity[XiaomiFeederCoordinator], SwitchEntity):
    """Base class for Xiaomi Feeder switches."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        """Initialize base switch."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=coordinator.device_name,
            manufacturer="Xiaomi",
            model=DEFAULT_MODEL,
        )


class XiaomiFeederScreenSleepSwitch(XiaomiFeederBaseSwitch):
    """Screen auto-sleep mode toggle."""

    _attr_translation_key = "screen_auto_sleep"
    _attr_icon = "mdi:cellphone-screenshot"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_screen_auto_sleep"
        self._attr_name = "Screen Auto Sleep"

    @property
    def is_on(self) -> Optional[bool]:
        if self.coordinator.data and self.coordinator.data.status:
            return self.coordinator.data.status.screen_auto_sleep
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_screen_auto_sleep(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_screen_auto_sleep(False)


class XiaomiFeederScreenProgressSwitch(XiaomiFeederBaseSwitch):
    """Screen light-up during feeding toggle."""

    _attr_translation_key = "screen_progress"
    _attr_icon = "mdi:monitor-eye"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_screen_progress"
        self._attr_name = "Screen Progress Light-up"

    @property
    def is_on(self) -> Optional[bool]:
        if self.coordinator.data and self.coordinator.data.status:
            return self.coordinator.data.status.screen_progress_display
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_screen_progress_display(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_screen_progress_display(False)


class XiaomiFeederChildLockSwitch(XiaomiFeederBaseSwitch):
    """Top physical button lock toggle."""

    _attr_translation_key = "child_lock"
    _attr_icon = "mdi:lock-outline"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_child_lock"
        self._attr_name = "Physical Child Lock"

    @property
    def is_on(self) -> Optional[bool]:
        if self.coordinator.data and self.coordinator.data.status:
            return self.coordinator.data.status.child_lock
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_child_lock(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_child_lock(False)


class XiaomiFeederAntiStackingSwitch(XiaomiFeederBaseSwitch):
    """Anti-stacking motor rotation toggle."""

    _attr_translation_key = "anti_stacking"
    _attr_icon = "mdi:rotate-left-variant"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_anti_stacking"
        self._attr_name = "Anti-Stacking Motor Mode"

    @property
    def is_on(self) -> Optional[bool]:
        if self.coordinator.data and self.coordinator.data.status:
            return self.coordinator.data.status.anti_stacking
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_anti_stacking(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_anti_stacking(False)


class XiaomiFeederGrainCompensationSwitch(XiaomiFeederBaseSwitch):
    """Grain weight compensation toggle."""

    _attr_translation_key = "grain_compensation"
    _attr_icon = "mdi:scale-unbalanced"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_grain_compensation"
        self._attr_name = "Grain Weight Compensation"

    @property
    def is_on(self) -> Optional[bool]:
        if self.coordinator.data and self.coordinator.data.status:
            return self.coordinator.data.status.grain_compensation
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_grain_compensation(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_grain_compensation(False)


class XiaomiFeederScheduleEnabledSwitch(XiaomiFeederBaseSwitch):
    """Master hardware schedule enable/disable switch."""

    _attr_translation_key = "schedule_enabled"
    _attr_icon = "mdi:calendar-check"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_schedule_enabled"
        self._attr_name = "Master Hardware Schedule"

    @property
    def is_on(self) -> Optional[bool]:
        if self.coordinator.data and self.coordinator.data.schedule:
            return self.coordinator.data.schedule.enabled
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_enable_hardware_schedule(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_enable_hardware_schedule(False)


class XiaomiFeederSkipNextMealSwitch(XiaomiFeederBaseSwitch):
    """Dynamic Skip Next Meal supervisor switch."""

    _attr_translation_key = "skip_next_meal"
    _attr_icon = "mdi:food-drumstick-off"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_skip_next_meal"
        self._attr_name = "Skip Next Meal"

    @property
    def is_on(self) -> bool:
        if self.coordinator.data:
            return self.coordinator.data.is_next_feed_skipped
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_skip_next_meal(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_skip_next_meal(False)


class XiaomiFeederRefillReminderSwitch(XiaomiFeederBaseSwitch):
    """Hopper refill reminder enable/disable switch."""

    _attr_translation_key = "refill_reminder"
    _attr_icon = "mdi:bell-ring-outline"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_refill_reminder"
        self._attr_name = "Refill Reminder"

    @property
    def is_on(self) -> Optional[bool]:
        if self.coordinator.data and self.coordinator.data.status:
            return self.coordinator.data.status.refill_reminder_enabled
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        hours = 6
        if self.coordinator.data and self.coordinator.data.status and self.coordinator.data.status.refill_reminder_hours:
            hours = self.coordinator.data.status.refill_reminder_hours
        await self.coordinator.async_set_refill_reminder(True, hours)

    async def async_turn_off(self, **kwargs: Any) -> None:
        hours = 6
        if self.coordinator.data and self.coordinator.data.status and self.coordinator.data.status.refill_reminder_hours:
            hours = self.coordinator.data.status.refill_reminder_hours
        await self.coordinator.async_set_refill_reminder(False, hours)


class XiaomiFeederIntakeAlarmSwitch(XiaomiFeederBaseSwitch):
    """Abnormal low food intake alert enable/disable switch."""

    _attr_translation_key = "intake_alarm"
    _attr_icon = "mdi:shield-alert-outline"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_intake_alarm"
        self._attr_name = "Low Intake Alarm"

    @property
    def is_on(self) -> Optional[bool]:
        if self.coordinator.data and self.coordinator.data.status:
            return self.coordinator.data.status.intake_alarm_enabled
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        threshold = 10
        if self.coordinator.data and self.coordinator.data.status and self.coordinator.data.status.intake_alarm_threshold:
            threshold = self.coordinator.data.status.intake_alarm_threshold
        await self.coordinator.async_set_intake_alarm(True, threshold)

    async def async_turn_off(self, **kwargs: Any) -> None:
        threshold = 10
        if self.coordinator.data and self.coordinator.data.status and self.coordinator.data.status.intake_alarm_threshold:
            threshold = self.coordinator.data.status.intake_alarm_threshold
        await self.coordinator.async_set_intake_alarm(False, threshold)
