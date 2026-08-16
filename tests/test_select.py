"""Tests for Xiaomi Feeder Select entities."""
from unittest.mock import AsyncMock, MagicMock
import pytest
from homeassistant.config_entries import ConfigEntry

from custom_components.xiaomi_feeder.const import FeederPIID, FeederSIID
from custom_components.xiaomi_feeder.coordinator import FeederCoordinatorData
from custom_components.xiaomi_feeder.select import XiaomiFeederScreenDisplaySelect
from xiaomi_feeder_2.models import FeederStatus, SchedulePlan


@pytest.fixture
def mock_entry():
    entry = MagicMock(spec=ConfigEntry)
    entry.entry_id = "test_entry_123"
    return entry


@pytest.fixture
def mock_coordinator(mock_entry):
    coord = MagicMock()
    coord.device_name = "Smart Feeder"
    coord.async_set_screen_display_mode = AsyncMock()
    return coord


def test_select_current_option_mapping(mock_coordinator, mock_entry):
    """Test screen display metric mapping from library status values."""
    select_entity = XiaomiFeederScreenDisplaySelect(mock_coordinator, mock_entry)

    # Test "Eaten-gram-display" -> "eaten"
    status_eaten = MagicMock(spec=FeederStatus)
    status_eaten.screen_display_mode = "Eaten-gram-display"
    status_eaten.raw_properties = {}
    mock_coordinator.data = FeederCoordinatorData(
        status=status_eaten,
        schedule=SchedulePlan(enabled=True, meals=[], raw_string=""),
    )
    assert select_entity.current_option == "eaten"

    # Test "Left-gram-display" -> "left"
    status_left = MagicMock(spec=FeederStatus)
    status_left.screen_display_mode = "Left-gram-display"
    status_left.raw_properties = {}
    mock_coordinator.data.status = status_left
    assert select_entity.current_option == "left"

    # Test "Percentage-display" -> "percentage"
    status_pct = MagicMock(spec=FeederStatus)
    status_pct.screen_display_mode = "Percentage-display"
    status_pct.raw_properties = {}
    mock_coordinator.data.status = status_pct
    assert select_entity.current_option == "percentage"


def test_select_current_option_raw_property_fallback(mock_coordinator, mock_entry):
    """Test fallback to raw properties if screen_display_mode is None."""
    select_entity = XiaomiFeederScreenDisplaySelect(mock_coordinator, mock_entry)

    status = MagicMock(spec=FeederStatus)
    status.screen_display_mode = None
    status.raw_properties = {
        f"{FeederSIID.CUSTOM}_{FeederPIID.SCREEN_DISPLAY}": 1
    }
    mock_coordinator.data = FeederCoordinatorData(
        status=status,
        schedule=SchedulePlan(enabled=True, meals=[], raw_string=""),
    )
    assert select_entity.current_option == "eaten"


@pytest.mark.asyncio
async def test_select_async_select_option(mock_coordinator, mock_entry):
    """Test selecting an option calls coordinator."""
    select_entity = XiaomiFeederScreenDisplaySelect(mock_coordinator, mock_entry)
    await select_entity.async_select_option("left")
    mock_coordinator.async_set_screen_display_mode.assert_awaited_once_with("left")
