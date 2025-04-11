"""Number platform for Balance Calibrator."""

from homeassistant.components.number import RestoreNumber
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: callable
):
    """Set up number platform."""
    async_add_entities(
        [
            BalanceSensitivityNumber(config_entry),
            BalanceMaxValueNumber(config_entry),
        ]
    )


class BalanceSensitivityNumber(RestoreNumber):
    """Representation of a Balance Calibrator Sensitivity Number Entity."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the number entity."""
        self._config_entry = config_entry

    @property
    def entry_data(self):
        """Return the entry data for this number."""
        return self.hass.data[DOMAIN][self._config_entry.entry_id]

    async def async_added_to_hass(self):
        """Restore state."""
        await super().async_added_to_hass()
        state = await self.async_get_last_number_data()
        if state:
            self.entry_data["sensitivity"] = state.native_value
            self.entry_data["update_sensor_callback"]()

    @property
    def name(self):
        """Return the name of the number entity."""
        return f"{self._config_entry.data['name']} Sensitivity"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._config_entry.entry_id}_sensitivity"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
        }

    @property
    def native_value(self):
        """Return the current sensitivity value."""
        return self.entry_data["sensitivity"]

    @property
    def native_min_value(self):
        """Return the minimum value."""
        return 0.1

    @property
    def native_max_value(self):
        """Return the maximum value."""
        return 2

    @property
    def native_step(self):
        """Return the step."""
        return 0.1

    async def async_set_native_value(self, value):
        """Set the sensitivity value."""
        self.entry_data["sensitivity"] = value
        # Trigger sensor update
        self.entry_data["update_sensor_callback"]()


class BalanceMaxValueNumber(RestoreNumber):
    """Representation of a Configuration Number Entity."""

    def __init__(self, config_entry) -> None:
        """Initialize the number entity."""
        self._config_entry = config_entry

    @property
    def entry_data(self):
        """Return the entry data for this number."""
        return self.hass.data[DOMAIN][self._config_entry.entry_id]

    async def async_added_to_hass(self):
        """Restore state."""
        await super().async_added_to_hass()
        state = await self.async_get_last_number_data()
        if state:
            self.entry_data["max_value"] = state.native_value
            self.entry_data["update_sensor_callback"]()

    @property
    def name(self):
        """Return the name of the number entity."""
        return f"{self._config_entry.data['name']} Max Value"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._config_entry.entry_id}_max_value"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
        }

    @property
    def native_value(self):
        """Return the current value."""
        return self.entry_data["max_value"]

    @property
    def native_min_value(self):
        """Return the minimum value."""
        return 1

    @property
    def native_max_value(self):
        """Return the maximum value."""
        return 100

    @property
    def native_step(self):
        """Return the step."""
        return 1

    async def async_set_native_value(self, value):
        """Set the max_value value."""
        self.entry_data["max_value"] = value
        # Trigger sensor update
        self.entry_data["update_sensor_callback"]()
