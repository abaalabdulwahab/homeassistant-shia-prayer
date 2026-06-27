"""
Hijri date calculator using Um Al-Qura algorithm
with adjustment from hmomen.com API.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, timedelta


HIJRI_MONTHS_AR = [
    "", "محرم", "صفر", "ربيع الأول", "ربيع الثاني",
    "جمادى الأولى", "جمادى الآخرة", "رجب", "شعبان",
    "رمضان", "شوال", "ذو القعدة", "ذو الحجة",
]

SHIA_EVENTS: dict[tuple[int, int], str] = {
    (1, 1):  "رأس السنة الهجرية",
    (1, 10): "يوم عاشوراء",
    (2, 20): "أربعين الإمام الحسين",
    (2, 28): "وفاة النبي محمد ﷺ / شهادة الإمام الحسن",
    (3, 8):  "شهادة الإمام الحسن العسكري",
    (3, 17): "ولادة النبي محمد ﷺ / ولادة الإمام الصادق",
    (6, 3):  "شهادة السيدة فاطمة الزهراء",
    (7, 13): "ولادة الإمام علي",
    (7, 27): "المبعث النبوي الشريف",
    (8, 15): "ولادة الإمام المهدي",
    (9, 1):  "بداية شهر رمضان",
    (9, 21): "شهادة الإمام علي",
    (10, 1): "عيد الفطر المبارك",
    (12, 10): "عيد الأضحى المبارك",
    (12, 18): "عيد الغدير",
    (12, 25): "ولادة الإمام علي الهادي",
}


@dataclass
class HijriDate:
    year: int
    month: int
    day: int
    adjustment: int = 0  # from hmomen API

    @property
    def month_name(self) -> str:
        return HIJRI_MONTHS_AR[self.month]

    @property
    def event(self) -> str | None:
        return SHIA_EVENTS.get((self.month, self.day))

    @property
    def full_date_ar(self) -> str:
        return f"{self.day} {self.month_name} {self.year} هـ"

    def to_dict(self) -> dict:
        return {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "month_name": self.month_name,
            "full_date": self.full_date_ar,
            "event": self.event or "",
            "adjustment": self.adjustment,
        }


def gregorian_to_hijri(g_date: date, adjustment_days: int = 0) -> HijriDate:
    """
    Convert Gregorian date to Hijri using standard algorithm.
    adjustment_days: value from hmomen API (adjustmentAmount).
    """
    g_date = g_date + timedelta(days=adjustment_days)

    y, m, d = g_date.year, g_date.month, g_date.day

    if m < 3:
        y -= 1
        m += 12

    a = math.floor(y / 100)
    b = 2 - a + math.floor(a / 4)

    jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5

    # JD to Hijri
    jd = jd - 0.5
    z = math.floor(jd + 0.5)

    l = z + 68569
    n = math.floor((4 * l) / 146097)
    l = l - math.floor((146097 * n + 3) / 4)
    i = math.floor((4000 * (l + 1)) / 1461001)
    l = l - math.floor((1461 * i) / 4) + 31
    j = math.floor((80 * l) / 2447)
    day = l - math.floor((2447 * j) / 80)
    l = math.floor(j / 11)
    month = j + 2 - 12 * l
    year = 100 * (n - 49) + i + l

    # Convert to Hijri
    jd_hijri = jd - 1948439.5 + 0.5
    year_h = math.floor((30 * jd_hijri + 10646) / 10631)
    jd_y = math.floor((11 * year_h + 3) / 30)
    month_h = math.ceil((jd_hijri - (354 * year_h) + (math.floor((11 * year_h + 3) / 30)) - 29) / 29.5) + 1
    if month_h > 12:
        month_h = 12
    day_h = int(jd_hijri - math.floor(29.5001 * (month_h - 1)) - (354 * year_h) + math.floor((11 * year_h + 3) / 30) - 29) + 1

    # Clamp values
    year_h = max(1, year_h)
    month_h = max(1, min(12, month_h))
    day_h = max(1, min(30, day_h))

    return HijriDate(year=year_h, month=month_h, day=day_h, adjustment=adjustment_days)
