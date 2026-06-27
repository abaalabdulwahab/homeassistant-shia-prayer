"""Hijri date model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class HijriDate:
    """Hijri date."""

    day: int
    month: int
    month_name: str
    year: int
    source: str