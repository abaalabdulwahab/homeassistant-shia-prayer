"""Constants for Shia Prayer."""

from datetime import timedelta

DOMAIN = "shia_prayer"
NAME = "Shia Prayer"
VERSION = "0.1.0"

DEFAULT_SCAN_INTERVAL = timedelta(minutes=15)

CONF_PROVIDER = "provider"

DEFAULT_PROVIDER = "auto"