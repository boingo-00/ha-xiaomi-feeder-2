"""Tests for Xiaomi Feeder Coordinator schedule algorithms and models."""
from datetime import datetime, timedelta
import pytest
from unittest.mock import MagicMock

from xiaomi_feeder_2.models import FeederStatus, ScheduleMeal, SchedulePlan


def calculate_next_feeding_helper(meals: list[ScheduleMeal], now: datetime) -> tuple[datetime | None, int | None]:
    """Pure calculation logic testing next feeding time."""
    if not meals:
        return None, None

    candidates = []
    for meal in meals:
        try:
            hour, minute = map(int, meal.time.split(":"))
        except Exception:
            continue

        for day_offset in range(8):
            check_date = now.date() + timedelta(days=day_offset)
            check_weekday = check_date.weekday()
            repeat_mask = meal.repeat
            day_bit = 1 << check_weekday
            is_scheduled_for_day = (repeat_mask == 0 and day_offset == 0) or bool(repeat_mask & day_bit)

            if is_scheduled_for_day:
                candidate_dt = datetime(check_date.year, check_date.month, check_date.day, hour, minute, tzinfo=now.tzinfo)
                if candidate_dt > now:
                    candidates.append((candidate_dt, meal.portions))
                    break

    if not candidates:
        return None, None

    candidates.sort(key=lambda x: x[0])
    return candidates[0][0], candidates[0][1]


def test_schedule_plan_parsing():
    """Test SchedulePlan model parsing."""
    plan = SchedulePlan(
        enabled=True,
        meals=[
            ScheduleMeal(time="08:00", portions=2, repeat=127, raw="0800027f"),
            ScheduleMeal(time="18:30", portions=3, repeat=127, raw="121e037f"),
        ],
        raw_string="0800027f121e037f",
    )
    assert plan.enabled is True
    assert len(plan.meals) == 2
    assert plan.meals[0].portions == 2
    assert plan.meals[1].time == "18:30"
    assert plan.to_dict()["raw_string"] == "0800027f121e037f"


def test_calculate_next_feeding_future():
    """Test calculating upcoming meal when time is in the morning."""
    from datetime import timezone
    now = datetime(2026, 8, 16, 7, 0, 0, tzinfo=timezone.utc)
    meals = [
        ScheduleMeal(time="08:00", portions=2, repeat=127, raw="0800027f"),
        ScheduleMeal(time="18:30", portions=3, repeat=127, raw="121e037f"),
    ]
    next_dt, portions = calculate_next_feeding_helper(meals, now)
    assert next_dt is not None
    assert next_dt.hour == 8
    assert next_dt.minute == 0
    assert portions == 2


def test_calculate_next_feeding_after_morning_meal():
    """Test calculating upcoming meal when morning meal passed."""
    from datetime import timezone
    now = datetime(2026, 8, 16, 12, 0, 0, tzinfo=timezone.utc)
    meals = [
        ScheduleMeal(time="08:00", portions=2, repeat=127, raw="0800027f"),
        ScheduleMeal(time="18:30", portions=3, repeat=127, raw="121e037f"),
    ]
    next_dt, portions = calculate_next_feeding_helper(meals, now)
    assert next_dt is not None
    assert next_dt.hour == 18
    assert next_dt.minute == 30
    assert portions == 3


def test_calculate_next_feeding_next_day():
    """Test calculating upcoming meal wrapping around to tomorrow."""
    from datetime import timezone
    now = datetime(2026, 8, 16, 20, 0, 0, tzinfo=timezone.utc)
    meals = [
        ScheduleMeal(time="08:00", portions=2, repeat=127, raw="0800027f"),
    ]
    next_dt, portions = calculate_next_feeding_helper(meals, now)
    assert next_dt is not None
    assert next_dt.day == 17
    assert next_dt.hour == 8
    assert portions == 2
