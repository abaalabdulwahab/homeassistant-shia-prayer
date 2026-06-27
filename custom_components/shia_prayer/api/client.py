"""
HTTP client for hmomen.com API.
Handles requests, caching, and error handling.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

BASE_URL = "https://hmomen.com"
APP_CONFIG_BASE = f"{BASE_URL}/app_config"

ENDPOINTS = {
    "hijri_adjustment": f"{APP_CONFIG_BASE}/android_hijridate_adjusment_umalqura.json",
    "ramadan_config":   f"{APP_CONFIG_BASE}/ramadan_config.json",
    "adhan_audio":      f"{APP_CONFIG_BASE}/adhana_audio_data.json",
}

CACHE_TTL = {
    "hijri_adjustment": timedelta(hours=6),
    "ramadan_config":   timedelta(hours=24),
    "adhan_audio":      timedelta(hours=24),
}

TIMEOUT = aiohttp.ClientTimeout(total=15)
USER_AGENT = "HaqibatElmomen/8.369 (Android; Home Assistant Integration)"


class HmomenApiClient:
    """Async HTTP client for hmomen.com with in-memory cache."""

    def __init__(self, session: aiohttp.ClientSession | None = None) -> None:
        self._session = session
        self._owns_session = session is None
        self._cache: dict[str, tuple[Any, datetime]] = {}

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=TIMEOUT,
                headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            )
        return self._session

    async def _fetch(self, url: str, cache_key: str) -> Any:
        """Fetch URL with caching."""
        # Check cache
        if cache_key in self._cache:
            data, cached_at = self._cache[cache_key]
            ttl = CACHE_TTL.get(cache_key, timedelta(hours=1))
            if datetime.now() - cached_at < ttl:
                _LOGGER.debug("Cache hit: %s", cache_key)
                return data

        session = await self._get_session()
        try:
            async with session.get(url) as resp:
                resp.raise_for_status()
                data = await resp.json(content_type=None)
                self._cache[cache_key] = (data, datetime.now())
                _LOGGER.debug("Fetched %s: %s", cache_key, str(data)[:100])
                return data
        except aiohttp.ClientResponseError as err:
            _LOGGER.error("HTTP %s for %s: %s", err.status, url, err.message)
            raise
        except aiohttp.ClientConnectionError as err:
            _LOGGER.error("Connection error for %s: %s", url, err)
            raise
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout fetching %s", url)
            raise

    async def get_hijri_adjustment(self) -> dict:
        """
        Returns:
            {
              "type": "forceDate" | "adjust",
              "adjustmentAmount": -1,
              "forcingValidUntil": "2026-06-16",
              "forcingDate": {"month": 12, "day": 30, "year": 1447}
            }
        """
        return await self._fetch(ENDPOINTS["hijri_adjustment"], "hijri_adjustment")

    async def get_ramadan_config(self) -> dict:
        """
        Returns:
            {
              "android_calendar_enabled": true,
              "ios_calendar_enabled": false,
              "correction": 0,
              "ios_correction": 2
            }
        """
        return await self._fetch(ENDPOINTS["ramadan_config"], "ramadan_config")

    async def get_adhan_audio(self) -> list:
        """
        Returns:
            [{"id": "adhan_1", "audio_url": "https://...", "name": "كريم منصوري"}, ...]
        """
        return await self._fetch(ENDPOINTS["adhan_audio"], "adhan_audio")

    def invalidate_cache(self, key: str | None = None) -> None:
        """Clear cache for a specific key or all keys."""
        if key:
            self._cache.pop(key, None)
        else:
            self._cache.clear()

    async def close(self) -> None:
        if self._owns_session and self._session and not self._session.closed:
            await self._session.close()
