"""Constants for Balance Calibrator."""

from homeassistant.const import Platform

DOMAIN = "balance_calibrator"
PLATFORMS = [Platform.BUTTON, Platform.NUMBER, Platform.SENSOR]

# Device info
MANUFACTURER = "Antek"
MODEL = "Balance Calibrator"
SW_VERSION = "1.0"

CONF_INPUT_ENTITY = "input_entity"
DEFAULT_SENSITIVITY = 0.2
DEAD_ZONE = 0.1
MIN_THRESHOLD = 10

ATTR_CENTER = "center"
ATTR_SENSITIVITY = "sensitivity"
ATTR_CALIBRATED = "calibrated"
ATTR_CALIBRATING = "calibrating"

DEFAULT_MAX_VALUE = 100
