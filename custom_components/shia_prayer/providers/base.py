"""Base provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Abstract base class for all Shia Prayer providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return provider name."""

    @abstractmethod
    async def async_get_prayer_times(self):
        """Return prayer times."""

    @abstractmethod
    async def async_get_hijri_date(self):
        """Return Hijri date."""

    @abstractmethod
    async def async_get_events(self):
        """Return today's events."""

    @abstractmethod
    async def async_health_check(self) -> bool:
        """Check provider availability."""