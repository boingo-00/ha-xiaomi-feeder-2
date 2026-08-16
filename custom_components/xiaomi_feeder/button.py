"""Button platform for Xiaomi Smart Pet Feeder 2."""
from __future__ import annotations

from homeassistant.components.button import ButtonEntity
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
    """Set up Xiaomi Feeder buttons."""
    coordinator: XiaomiFeederCoordinator = hass.data[DOMAIN][entry.entry_id]

    buttons: list[ButtonEntity] = [
        XiaomiFeederFeedButton(coordinator, entry),
        XiaomiFeederTareScaleButton(coordinator, entry),
        XiaomiFeederResetDesiccantButton(coordinator, entry),
        XiaomiFeederClearRefillAlertButton(coordinator, entry),
        XiaomiFeederClearIntakeAlertButton(coordinator, entry),
        XiaomiFeederClearScheduleButton(coordinator, entry),
    ]

    async_add_entities(buttons)


class XiaomiFeederBaseButton(CoordinatorEntity[XiaomiFeederCoordinator], ButtonEntity):
    """Base class for Xiaomi Feeder buttons."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        """Initialize base button."""
        super().__init__(coordinator)
        self.entry = entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=coordinator.device_name,
            manufacturer="Xiaomi",
            model=DEFAULT_MODEL,
        )


class XiaomiFeederFeedButton(XiaomiFeederBaseButton):
    """Manual feed trigger button."""

    _attr_translation_key = "feed"
    _attr_icon = "mdi:food-drumstick"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_feed"
        self._attr_name = "Feed"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.async_feed()


class XiaomiFeederTareScaleButton(XiaomiFeederBaseButton):
    """Scale tare / calibration button."""

    _attr_translation_key = "tare_scale"
    _attr_icon = "mdi:scale-balance"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_tare_scale"
        self._attr_name = "Tare Scale"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.async_calibrate_scale()


class XiaomiFeederResetDesiccantButton(XiaomiFeederBaseButton):
    """Reset desiccant timer button."""

    _attr_translation_key = "reset_desiccant"
    _attr_icon = "mdi:refresh"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_reset_desiccant"
        self._attr_name = "Reset Desiccant Timer"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.async_reset_desiccant()


class XiaomiFeederClearRefillAlertButton(XiaomiFeederBaseButton):
    """Clear refill alert button."""

    _attr_translation_key = "clear_refill_alert"
    _attr_icon = "mdi:bell-cancel"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_clear_refill_alert"
        self._attr_name = "Clear Refill Alert"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.async_clear_refill_alert()


class XiaomiFeederClearIntakeAlertButton(XiaomiFeederBaseButton):
    """Clear low intake alert button."""

    _attr_translation_key = "clear_intake_alert"
    _attr_icon = "mdi:shield-check"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_clear_intake_alert"
        self._attr_name = "Clear Low Intake Alert"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.async_clear_intake_alert()


class XiaomiFeederClearScheduleButton(XiaomiFeederBaseButton):
    """Clear all schedules button."""

    _attr_translation_key = "clear_schedule"
    _attr_icon = "mdi:calendar-remove"

    def __init__(self, coordinator: XiaomiFeederCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_clear_schedule"
        self._attr_name = "Clear Hardware Schedule"

    async def async_press(self) -> None:
        """Handle button press."""
        await self.coordinator.async_clear_hardware_schedule()
