"""Demo provider."""

from __future__ import annotations

from .base import BaseProvider


class DemoProvider(BaseProvider):
    """Temporary provider."""

    @property
    def name(self) -> str:
        return "Demo"

    async def async_get_prayer_times(self):
        return None

    async def async_get_hijri_date(self):
        return None

    async def async_get_events(self):
        return []

    async def async_health_check(self) -> bool:
        return True