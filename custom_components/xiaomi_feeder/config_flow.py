"""Config flow for Xiaomi Smart Pet Feeder 2 integration."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.data_entry_flow import FlowResult
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv, selector

from xiaomi_feeder_2 import XiaomiFeeder, XiaomiFeederError

from .const import CONF_IP, DEFAULT_MODEL, DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)

DAY_OPTIONS = [
    {"value": "mon", "label": "Monday"},
    {"value": "tue", "label": "Tuesday"},
    {"value": "wed", "label": "Wednesday"},
    {"value": "thu", "label": "Thursday"},
    {"value": "fri", "label": "Friday"},
    {"value": "sat", "label": "Saturday"},
    {"value": "sun", "label": "Sunday"},
]
DAY_KEYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def repeat_to_days(repeat: int) -> list[str]:
    """Convert bitmask integer to list of weekday keys."""
    if repeat == 0:
        return []
    return [DAY_KEYS[i] for i in range(7) if (repeat & (1 << i))]


def days_to_repeat(days: list[str]) -> int:
    """Convert list of weekday keys to repeat bitmask integer."""
    if not days:
        return 0  # 0 means one-time today
    mask = 0
    for day in days:
        if day in DAY_KEYS:
            mask |= 1 << DAY_KEYS.index(day)
    return mask


def serialize_meals(meals: list[dict[str, Any]], enabled: bool = True) -> str:
    """Serialize meal dictionaries into feeder EEPROM payload string [1,HHMMPPSS,...]."""
    if not meals:
        return "[0]"
    sorted_meals = sorted(meals, key=lambda m: m["time"])
    encoded = []
    for m in sorted_meals:
        parts = m["time"].split(":")
        h = int(parts[0])
        minute = int(parts[1])
        p = int(m["portions"])
        # Hardware uses 2 digits: 01=active/daily, 00=disabled
        status = 1 if m.get("enabled", True) and int(m.get("repeat", 1)) > 0 else 0
        encoded.append(f"{h:02d}{minute:02d}{p:02d}{status:02d}")
    return f"[1,{','.join(encoded)}]"


class XiaomiFeederConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Xiaomi Smart Pet Feeder 2."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return XiaomiFeederOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            ip = user_input[CONF_IP].strip()
            token = user_input[CONF_TOKEN].strip()
            name = user_input.get(CONF_NAME, DEFAULT_NAME).strip()

            # Test connection to device
            try:
                client = XiaomiFeeder(ip, token, timeout=5)
                status = await self.hass.async_add_executor_job(client.status)
                
                # Check unique_id based on IP or serial
                unique_id = f"xiaomi_feeder_{ip.replace('.', '_')}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=name,
                    data={
                        CONF_IP: ip,
                        CONF_TOKEN: token,
                        CONF_NAME: name,
                        "model": DEFAULT_MODEL,
                    },
                )
            except XiaomiFeederError as err:
                _LOGGER.error("Cannot connect to Xiaomi Feeder at %s: %s", ip, err)
                errors["base"] = "cannot_connect"
            except Exception as err:
                _LOGGER.exception("Unexpected exception during config flow: %s", err)
                errors["base"] = "unknown"

        schema = vol.Schema(
            {
                vol.Required(CONF_IP): cv.string,
                vol.Required(CONF_TOKEN): cv.string,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )


class XiaomiFeederOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for managing Xiaomi Feeder hardware schedules and settings."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._selected_meal_idx: Optional[int] = None

    def _get_coordinator(self):
        """Get the active feeder coordinator."""
        return self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id)

    def _get_current_meals(self) -> tuple[list[dict[str, Any]], bool]:
        """Get list of current meals and master schedule switch state from coordinator."""
        coord = self._get_coordinator()
        if not coord or not coord.data or not coord.data.schedule:
            return [], True
        sched = coord.data.schedule
        meals = [
            {
                "time": m.time,
                "portions": m.portions,
                "repeat": m.repeat,
                "raw": m.raw,
            }
            for m in sched.meals
        ]
        return meals, sched.enabled

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the options menu and show current schedule overview."""
        meals, enabled = self._get_current_meals()
        menu_options = ["add_meal"]
        if meals:
            menu_options.extend(["edit_select", "delete_select", "clear_all"])

        if meals:
            total_portions = sum(m["portions"] for m in meals)
            lines = [
                "### 📋 Current Active Schedule",
                "",
            ]
            for idx, m in enumerate(meals, 1):
                portions_text = f"{m['portions']} portion{'s' if m['portions'] > 1 else ''}"
                lines.append(f"• **Meal {idx}:** `{m['time']}` — **{portions_text}** (≈ {m['portions'] * 10}–{m['portions'] * 15}g)")
            
            lines.append(f"\n**Total Daily Intake:** {total_portions} portions (≈ {total_portions * 10}–{total_portions * 15}g)")
            if not enabled:
                lines.append("\n⚠️ *Notice: Hardware Schedule master switch is currently disabled.*")
            schedule_summary = "\n".join(lines)
        else:
            schedule_summary = "ℹ️ *No offline feeding meals currently stored in device memory.*"

        return self.async_show_menu(
            step_id="init",
            menu_options=menu_options,
            description_placeholders={"schedule_summary": schedule_summary},
        )

    async def async_step_add_meal(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Add a new scheduled meal directly to EEPROM."""
        if user_input is not None:
            coord = self._get_coordinator()
            meals, enabled = self._get_current_meals()

            raw_time = str(user_input["time"])[:5]  # "08:00"
            portions = int(user_input.get("portions", 2))

            meals.append({
                "time": raw_time,
                "portions": portions,
                "repeat": 1,
            })

            payload = serialize_meals(meals, enabled)
            if coord:
                await coord.async_write_hardware_schedule(payload)

            return self.async_create_entry(title="", data={})

        schema = vol.Schema(
            {
                vol.Required("time", default="08:00:00"): selector.TimeSelector(),
                vol.Required(
                    "portions", default=2
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1, max=15, step=1, mode=selector.NumberSelectorMode.BOX
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="add_meal",
            data_schema=schema,
        )

    async def async_step_edit_select(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Select which meal to edit."""
        meals, _ = self._get_current_meals()
        if not meals:
            return await self.async_step_init()

        if user_input is not None:
            self._selected_meal_idx = int(user_input["meal_index"])
            return await self.async_step_edit_meal()

        meal_options = [
            {
                "value": str(idx),
                "label": f"Meal {idx+1}: {m['time']} — {m['portions']} portion{'s' if m['portions'] > 1 else ''} (≈ {m['portions'] * 10}–{m['portions'] * 15}g)",
            }
            for idx, m in enumerate(meals)
        ]

        schema = vol.Schema(
            {
                vol.Required("meal_index", default="0"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=meal_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="edit_select",
            data_schema=schema,
        )

    async def async_step_edit_meal(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Edit the selected meal."""
        meals, enabled = self._get_current_meals()
        idx = self._selected_meal_idx
        if idx is None or idx < 0 or idx >= len(meals):
            return await self.async_step_init()

        target_meal = meals[idx]

        if user_input is not None:
            coord = self._get_coordinator()
            raw_time = str(user_input["time"])[:5]
            portions = int(user_input.get("portions", target_meal["portions"]))

            meals[idx] = {
                "time": raw_time,
                "portions": portions,
                "repeat": 1,
            }

            payload = serialize_meals(meals, enabled)
            if coord:
                await coord.async_write_hardware_schedule(payload)

            return self.async_create_entry(title="", data={})

        default_time = f"{target_meal['time']}:00" if len(target_meal['time']) == 5 else target_meal['time']

        schema = vol.Schema(
            {
                vol.Required("time", default=default_time): selector.TimeSelector(),
                vol.Required(
                    "portions", default=target_meal["portions"]
                ): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=1, max=15, step=1, mode=selector.NumberSelectorMode.BOX
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="edit_meal",
            data_schema=schema,
        )

    async def async_step_delete_select(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Select which meal to delete."""
        meals, enabled = self._get_current_meals()
        if not meals:
            return await self.async_step_init()

        if user_input is not None:
            coord = self._get_coordinator()
            del_idx = int(user_input["meal_index"])
            if 0 <= del_idx < len(meals):
                meals.pop(del_idx)
                payload = serialize_meals(meals, enabled)
                if coord:
                    await coord.async_write_hardware_schedule(payload)

            return self.async_create_entry(title="", data={})

        meal_options = [
            {
                "value": str(idx),
                "label": f"{m['time']} — {m['portions']} portion(s)",
            }
            for idx, m in enumerate(meals)
        ]

        schema = vol.Schema(
            {
                vol.Required("meal_index", default="0"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=meal_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="delete_select",
            data_schema=schema,
        )

    async def async_step_clear_all(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Confirm clearing all hardware schedules."""
        if user_input is not None:
            coord = self._get_coordinator()
            if coord:
                await coord.async_clear_hardware_schedule()
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="clear_all",
            data_schema=vol.Schema({}),
        )

