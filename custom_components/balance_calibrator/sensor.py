"""Sensor platform for Balance Calibrator."""

from homeassistant.components.sensor import RestoreSensor, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    ATTR_CALIBRATED,
    ATTR_CALIBRATING,
    ATTR_CENTER,
    DEAD_ZONE,
    DOMAIN,
    MANUFACTURER,
    MIN_THRESHOLD,
    MODEL,
    SW_VERSION,
)


async def async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry, async_add_entities: callable
):
    """Set up sensor platform."""
    async_add_entities(
        [
            CalibratedBalanceSensor(config_entry),
            CenterSensor(config_entry),
        ]
    )


class CalibratedBalanceSensor(SensorEntity):
    """Representation of a Balance Calibrator Sensor."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        self._config_entry = config_entry
        self._state = 0
        self._calibration_min = None
        self._calibration_max = None

    @property
    def entry_data(self):
        """Return the entry data for this sensor."""
        return self.hass.data[DOMAIN][self._config_entry.entry_id]

    async def async_added_to_hass(self):
        """Register callbacks."""
        await super().async_added_to_hass()

        async_track_state_change_event(
            self.hass, [self.entry_data["input_entity"]], self._async_input_changed
        )
        self.hass.data[DOMAIN][self._config_entry.entry_id][
            "stop_calibration_callback"
        ] = self.stop_calibration
        self.hass.data[DOMAIN][self._config_entry.entry_id][
            "start_calibration_callback"
        ] = self.start_calibration
        self.hass.data[DOMAIN][self._config_entry.entry_id][
            "update_sensor_callback"
        ] = self._update_state

    @callback
    def _async_input_changed(self, event):
        new_state = event.data.get("new_state")
        if new_state is None:
            return

        try:
            value = float(new_state.state)
        except (ValueError, TypeError):
            return

        entry_data = self.entry_data

        if entry_data["calibrating"]:
            self._calibration_min = min(self._calibration_min or value, value)
            self._calibration_max = max(self._calibration_max or value, value)
            self._update_state(0)
            self.async_write_ha_state()
            return

        self._update_state(value)

    def start_calibration(self):
        """Start calibration."""
        entry_data = self.entry_data
        entry_data["calibrating"] = True
        entry_data["center"] = None
        self._calibration_min = float(
            self.hass.states.get(entry_data["input_entity"]).state
        )
        self._calibration_max = float(
            self.hass.states.get(entry_data["input_entity"]).state
        )

        # Reset the state to 0 during calibration
        self._state = 0

        self.async_write_ha_state()
        # Trigger sensor update
        # This will reset the state to 0 during calibration

    def stop_calibration(self):
        """Stop calibration."""
        entry_data = self.entry_data
        entry_data["calibrating"] = False
        if self._calibration_min is not None and self._calibration_max is not None:
            entry_data["center"] = (self._calibration_min + self._calibration_max) / 2
            self._calibration_min = None
            self._calibration_max = None

        self.entry_data["update_center_callback"]()
        self._update_state()

    def _update_state(self, value=None):
        """Update the sensor state."""
        if value is None:
            # If no value is provided, use the last known state
            value = float(self.hass.states.get(self.entry_data["input_entity"]).state)
            if value is None:
                return
        entry_data = self.entry_data
        if entry_data["center"] is None:
            # If center is not set, we can't calculate the state
            self._state = 0
            self.async_write_ha_state()
            return

        # Calculation logic using entry_data
        distance = abs(value - entry_data["center"])
        if distance <= DEAD_ZONE:
            self._state = entry_data["max_value"]
        else:
            # Calculate the state based on distance and sensitivity
            self._state = entry_data["max_value"] / (
                1 + entry_data["sensitivity"] * distance**1.7
            )

        # Ensure the state is within the valid range
        self._state = (
            max(0, min(entry_data["max_value"], self._state))
            if self._state > MIN_THRESHOLD
            else 0
        )

        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._config_entry.data['name']} Calibrated Balance"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return round(self._state)

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._config_entry.entry_id}_sensor"

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._config_entry.entry_id)},
            "manufacturer": MANUFACTURER,
            "model": MODEL,
            "name": self._config_entry.data["name"],
            "sw_version": SW_VERSION,
        }

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        entry_data = self.entry_data
        return {
            ATTR_CENTER: entry_data["center"],
            ATTR_CALIBRATED: entry_data["center"] is not None,
            ATTR_CALIBRATING: entry_data["calibrating"],
        }


class CenterSensor(RestoreSensor):
    """Representation of a Center Sensor."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        self._config_entry = config_entry

    @property
    def entry_data(self):
        """Return the entry data for this sensor."""
        return self.hass.data[DOMAIN][self._config_entry.entry_id]

    async def async_added_to_hass(self):
        """Register callbacks."""
        await super().async_added_to_hass()
        old_val = await self.async_get_last_sensor_data()
        if old_val:
            self.entry_data["center"] = old_val.native_value
            self.entry_data["update_center_callback"] = self._update_state
            self.entry_data["update_sensor_callback"]()

    @callback
    def _update_state(self):
        """Update the sensor state."""
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self._config_entry.data['name']} Center"

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._config_entry.entry_id}_center_sensor"

    @property
    def device_info(self):
        """Return device info."""
        return {"identifiers": {(DOMAIN, self._config_entry.entry_id)}}

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.entry_data["center"]
