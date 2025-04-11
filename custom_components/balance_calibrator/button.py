"""Button components for Balance Calibrator."""

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import async_call_later

from .const import ATTR_CALIBRATING, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities
):
    """Set up button platform."""
    async_add_entities([BalanceCalibrationButton(hass, config_entry)])


class BalanceCalibrationButton(ButtonEntity):
    """Representation of a Balance Calibration Button."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize the button entity."""
        self.hass = hass
        self._config_entry = config_entry

    @property
    def entry_data(self):
        """Return the entry data for this button."""
        return self.hass.data[DOMAIN][self._config_entry.entry_id]

    @property
    def name(self):
        """Return the name of the number entity."""
        return f"{self._config_entry.data['name']} Calibration"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._config_entry.entry_id}_calibration_button"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
        }

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        entry_data = self.entry_data
        return {
            ATTR_CALIBRATING: entry_data["calibrating"],
        }

    async def async_press(self):
        """Handle button press."""
        entry_data = self.entry_data
        entry_data["start_calibration_callback"]()

        registry = er.async_get(self.hass)
        sensor_entity_id = registry.async_get_entity_id(
            "sensor", DOMAIN, f"{self._config_entry.entry_id}_sensor"
        )
        if not sensor_entity_id:
            return

        async def stop_calibration(_):
            entry_data["stop_calibration_callback"]()

        entry_data["unsub_calibration"] = async_call_later(
            self.hass, 5, stop_calibration
        )
