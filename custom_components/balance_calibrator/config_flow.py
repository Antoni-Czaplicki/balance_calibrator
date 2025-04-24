"""Config flow for Balance Calibrator integration."""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import CONF_INPUT_ENTITY, DOMAIN


class BalanceCalibratorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Balance Calibrator."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Check for existing entries with the same name
            existing_entries = self.hass.config_entries.async_entries(DOMAIN)
            for entry in existing_entries:
                if entry.data.get(CONF_NAME) == user_input[CONF_NAME]:
                    errors[CONF_NAME] = "already_configured"
                    break

            if not errors:
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

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

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return BalanceCalibratorOptionsFlow(config_entry)


class BalanceCalibratorOptionsFlow(config_entries.OptionsFlow):
    """Handle an options flow for Balance Calibrator."""

    def __init__(self, config_entry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={
                    **self.config_entry.data,
                    CONF_INPUT_ENTITY: user_input[CONF_INPUT_ENTITY],
                },
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_INPUT_ENTITY,
                        default=self.config_entry.data.get(CONF_INPUT_ENTITY),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["sensor", "number", "input_number"]
                        )
                    ),
                }
            ),
        )
