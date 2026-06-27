"""DataUpdateCoordinator for Shia Prayer."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class ShiaPrayerCoordinator(DataUpdateCoordinator):
    """Coordinator for Shia Prayer."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Shia Prayer",
            update_interval=DEFAULT_SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        """Fetch data from provider."""

        #
        # في المرحلة الحالية سنعيد بيانات تجريبية.
        # في الإصدار القادم سنربط Provider Manager هنا.
        #

        return {
            "status": "ok",
            "provider": "none",
        }