"""
Provider: حقيبة المؤمن (Haqibat Al-Momen)
Source: hmomen.com

Provides:
- Hijri date (with adjustment from API)
- Today's Islamic event
- Prayer times (calculated locally)
- Ramadan status
"""
from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any

from ..api.client import HmomenApiClient
from ..api.hijri import gregorian_to_hijri, HijriDate
from ..api.prayer_calc import calculate_prayer_times, PrayerTimes

_LOGGER = logging.getLogger(__name__)

PROVIDER_NAME = "haqibat"
PROVIDER_LABEL = "حقيبة المؤمن"


class HaqibatProvider:
    """
    Data provider backed by hmomen.com static config files.
    Prayer times are calculated locally.
    Hijri date adjustment is fetched from API.
    """

    def __init__(
        self,
        latitude: float,
        longitude: float,
        timezone_offset: float,
        client: HmomenApiClient | None = None,
    ) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.timezone_offset = timezone_offset
        self._client = client or HmomenApiClient()
        self._adjustment: int = 0  # days, from API

    # ── Public API ────────────────────────────────────────────────────────────

    async def async_update(self) -> dict[str, Any]:
        """Fetch API data and compute all values. Returns sensor data dict."""
        today = date.today()
        now   = datetime.now()

        # 1. Fetch hijri adjustment from API
        try:
            adj_data = await self._client.get_hijri_adjustment()
            self._adjustment = adj_data.get("adjustmentAmount", 0)
            _LOGGER.debug("Hijri adjustment from API: %d", self._adjustment)
        except Exception as err:
            _LOGGER.warning("Could not fetch hijri adjustment: %s — using %d", err, self._adjustment)

        # 2. Fetch ramadan config
        ramadan_correction = 0
        try:
            ram_data = await self._client.get_ramadan_config()
            ramadan_correction = ram_data.get("correction", 0)
        except Exception as err:
            _LOGGER.warning("Could not fetch ramadan config: %s", err)

        # 3. Calculate hijri date
        hijri = gregorian_to_hijri(today, adjustment_days=self._adjustment)

        # 4. Calculate prayer times locally
        prayers = calculate_prayer_times(
            target_date=today,
            latitude=self.latitude,
            longitude=self.longitude,
            timezone_offset=self.timezone_offset,
        )

        # 5. Next prayer
        next_p = prayers.next_prayer(now)
        next_prayer_name = next_p[0] if next_p else ""
        next_prayer_time = next_p[1].strftime("%H:%M") if next_p else ""

        return {
            # Hijri date
            "hijri_date":       hijri.full_date_ar,
            "hijri_day":        hijri.day,
            "hijri_month":      hijri.month,
            "hijri_month_name": hijri.month_name,
            "hijri_year":       hijri.year,
            "hijri_adjustment": self._adjustment,

            # Islamic event
            "today_event": hijri.event or "",

            # Prayer times (strings HH:MM)
            **{f"prayer_{k}": v for k, v in prayers.to_dict().items()},

            # Next prayer
            "next_prayer_name": next_prayer_name,
            "next_prayer_time": next_prayer_time,

            # Ramadan
            "is_ramadan":          hijri.month == 9,
            "ramadan_correction":  ramadan_correction,

            # Provider meta
            "provider": PROVIDER_LABEL,
            "source":   "hmomen.com",
        }

    async def async_get_adhan_list(self) -> list[dict]:
        """Return list of available adhan audio tracks."""
        try:
            return await self._client.get_adhan_audio()
        except Exception as err:
            _LOGGER.warning("Could not fetch adhan list: %s", err)
            return []

    async def close(self) -> None:
        await self._client.close()
