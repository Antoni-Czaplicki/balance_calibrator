"""The Balance Calibrator integration."""

from homeassistant.core import HomeAssistant

from .const import CONF_INPUT_ENTITY, DEFAULT_MAX_VALUE, DOMAIN, PLATFORMS


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
