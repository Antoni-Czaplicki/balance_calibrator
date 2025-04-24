"""The Balance Calibrator integration."""

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_INPUT_ENTITY, DEFAULT_MAX_VALUE, DOMAIN

PLATFORMS = [Platform.BUTTON, Platform.NUMBER, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry):
    """Set up balance calibrator from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Initialize state storage
    entry_id = entry.entry_id
    hass.data[DOMAIN][entry_id] = {
        "center": None,
        "sensitivity": 0.2,
        "calibrating": False,
        "max_value": DEFAULT_MAX_VALUE,
        "input_entity": entry.data[CONF_INPUT_ENTITY],
        "sensor_entity": None,
        "unsub_calibration": None,
        "stop_calibration_callback": lambda: None,
        "start_calibration_callback": lambda: None,
        "update_sensor_callback": lambda: None,
    }

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
