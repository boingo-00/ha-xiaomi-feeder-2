"""Config flow for Xiaomi Smart Pet Feeder 2 integration."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from xiaomi_feeder_2 import XiaomiFeeder, XiaomiFeederError

from .const import CONF_IP, DEFAULT_MODEL, DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


class XiaomiFeederConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Xiaomi Smart Pet Feeder 2."""

    VERSION = 1

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
