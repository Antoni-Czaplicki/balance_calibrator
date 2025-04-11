"""Config flow for Balance Calibrator integration."""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers import selector

from .const import CONF_INPUT_ENTITY, DOMAIN


class BalanceCalibratorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Balance Calibrator."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_INPUT_ENTITY])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Required(CONF_INPUT_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["sensor", "number", "input_number"]
                        )
                    ),
                }
            ),
            errors=errors,
        )
