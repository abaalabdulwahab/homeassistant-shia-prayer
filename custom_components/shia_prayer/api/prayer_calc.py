"""
Prayer time calculator - fully local, no internet required.
Uses standard astronomical formulas with Shia (Jaafari) method.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta


# ── حساب الصلاة الجعفري ──────────────────────────────────────────────────────
# Fajr:   18° depression (University of Islamic Sciences, Karachi - Shia variant)
# Isha:   14° depression
# Maghrib: 4° after sunset (Shia jurisprudence — sun disk + 4°)
# ─────────────────────────────────────────────────────────────────────────────

FAJR_ANGLE = 16.0    # درجة الفجر الجعفري
ISHA_ANGLE  = 14.0   # درجة العشاء


@dataclass
class PrayerTimes:
    fajr:    datetime
    sunrise: datetime
    dhuhr:   datetime
    asr:     datetime
    maghrib: datetime
    isha:    datetime

    def to_dict(self) -> dict:
        fmt = "%H:%M"
        return {
            "fajr":    self.fajr.strftime(fmt),
            "sunrise": self.sunrise.strftime(fmt),
            "dhuhr":   self.dhuhr.strftime(fmt),
            "asr":     self.asr.strftime(fmt),
            "maghrib": self.maghrib.strftime(fmt),
            "isha":    self.isha.strftime(fmt),
        }

    def as_datetimes(self) -> dict:
        return {
            "fajr":    self.fajr,
            "sunrise": self.sunrise,
            "dhuhr":   self.dhuhr,
            "asr":     self.asr,
            "maghrib": self.maghrib,
            "isha":    self.isha,
        }

    def next_prayer(self, now: datetime) -> tuple[str, datetime] | None:
        """Return (name, time) of the next prayer after `now`."""
        names_ar = {
            "fajr": "الفجر", "sunrise": "الشروق", "dhuhr": "الظهر",
            "asr": "العصر", "maghrib": "المغرب", "isha": "العشاء",
        }
        for key, dt in self.as_datetimes().items():
            if dt > now:
                return names_ar[key], dt
        return None


def _deg2rad(d: float) -> float:
    return d * math.pi / 180.0

def _rad2deg(r: float) -> float:
    return r * 180.0 / math.pi

def _fix_hour(h: float) -> float:
    h = h - 24.0 * math.floor(h / 24.0)
    return h

def _sun_position(julian_date: float) -> tuple[float, float]:
    """Return (declination, equation_of_time) for given Julian Date."""
    d = julian_date - 2451545.0
    g = 357.529 + 0.98560028 * d
    q = 280.459 + 0.98564736 * d
    l = q + 1.915 * math.sin(_deg2rad(g)) + 0.020 * math.sin(_deg2rad(2 * g))
    e = 23.439 - 0.00000036 * d
    ra = _rad2deg(math.atan2(math.cos(_deg2rad(e)) * math.sin(_deg2rad(l)), math.cos(_deg2rad(l)))) / 15.0
    ra = _fix_hour(ra)
    dec = _rad2deg(math.asin(math.sin(_deg2rad(e)) * math.sin(_deg2rad(l))))
    eqt = q / 15.0 - ra
    return dec, eqt


def _julian_date(year: int, month: int, day: int) -> float:
    if month <= 2:
        year -= 1
        month += 12
    a = math.floor(year / 100.0)
    b = 2 - a + math.floor(a / 4.0)
    return math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + b - 1524.5


def _hour_angle(lat: float, dec: float, angle: float) -> float | None:
    """Return hour angle for given depression angle. None if sun never reaches."""
    cos_h = (-math.sin(_deg2rad(angle)) - math.sin(_deg2rad(lat)) * math.sin(_deg2rad(dec))) / \
            (math.cos(_deg2rad(lat)) * math.cos(_deg2rad(dec)))
    if abs(cos_h) > 1:
        return None
    return _rad2deg(math.acos(cos_h)) / 15.0


def calculate_prayer_times(
    target_date: date,
    latitude: float,
    longitude: float,
    timezone_offset: float,  # e.g. 3.0 for UTC+3 (Saudi Arabia)
) -> PrayerTimes:
    """
    Calculate Shia (Jaafari) prayer times for a given date and location.

    Args:
        target_date: The date to calculate for.
        latitude: Location latitude (e.g. 25.3 for Riyadh).
        longitude: Location longitude (e.g. 46.7 for Riyadh).
        timezone_offset: Hours offset from UTC (e.g. 3.0 for KSA).

    Returns:
        PrayerTimes with all 6 prayer/sun times as datetime objects.
    """
    jd = _julian_date(target_date.year, target_date.month, target_date.day)
    dec, eqt = _sun_position(jd + 0.5 - longitude / 360.0)

    # Solar noon
    noon = 12.0 - longitude / 15.0 - eqt + timezone_offset

    def to_dt(hour_float: float) -> datetime:
        h = int(hour_float)
        m = int((hour_float - h) * 60)
        s = int(((hour_float - h) * 60 - m) * 60)
        # Clamp
        h = max(0, min(23, h))
        m = max(0, min(59, m))
        s = max(0, min(59, s))
        return datetime(target_date.year, target_date.month, target_date.day, h, m, s)

    # Sunrise / Sunset (0.833° = standard refraction + solar disk)
    ha_sunrise = _hour_angle(latitude, dec, -0.833)
    sunrise_h  = noon - (ha_sunrise or 6.0)
    sunset_h   = noon + (ha_sunrise or 6.0)

    # Fajr
    ha_fajr = _hour_angle(latitude, dec, FAJR_ANGLE)
    fajr_h  = noon - (ha_fajr or 8.0)

    # Isha
    ha_isha = _hour_angle(latitude, dec, ISHA_ANGLE)
    isha_h  = noon + (ha_isha or 7.5)

    # Dhuhr = solar noon + 1 min (after zawaal)
    dhuhr_h = noon + (1.0 / 60.0)

    # Asr (Shia = shadow = 1x object length from noon shadow)
    t_asr = _rad2deg(math.atan(1.0 / (1.0 + math.tan(_deg2rad(abs(latitude - dec)))))) / 15.0
    asr_h = noon + t_asr

    # Maghrib (Shia = after redness disappears ~ 15-17 min after sunset)
    # Standard Shia: when sun disk is hidden + 4° (≈ 16 min after sunset)
    ha_magh = _hour_angle(latitude, dec, -4.0)
    maghrib_h = noon + (ha_magh or 6.5)

    return PrayerTimes(
        fajr    = to_dt(fajr_h),
        sunrise = to_dt(sunrise_h),
        dhuhr   = to_dt(dhuhr_h),
        asr     = to_dt(asr_h),
        maghrib = to_dt(maghrib_h),
        isha    = to_dt(isha_h),
    )
