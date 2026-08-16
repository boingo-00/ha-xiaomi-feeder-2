"""Tests for Xiaomi Feeder Sensor entities."""
from unittest.mock import MagicMock
import pytest
from homeassistant.config_entries import ConfigEntry

from custom_components.xiaomi_feeder.coordinator import FeederCoordinatorData
from custom_components.xiaomi_feeder.sensor import XiaomiFeederTargetPortionsSensor
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
    return coord


def test_target_portions_sensor(mock_coordinator, mock_entry):
    """Test reading target portions telemetry value."""
    sensor = XiaomiFeederTargetPortionsSensor(mock_coordinator, mock_entry)

    status = MagicMock(spec=FeederStatus)
    status.target_feeding_portions = 2
    mock_coordinator.data = FeederCoordinatorData(
        status=status,
        schedule=SchedulePlan(enabled=True, meals=[], raw_string=""),
    )

    assert sensor.native_value == 2
