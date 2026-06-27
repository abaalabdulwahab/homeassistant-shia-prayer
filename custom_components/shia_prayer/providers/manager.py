"""Provider manager."""

from __future__ import annotations

from .base import BaseProvider


class ProviderManager:
    """Manage prayer data providers."""

    def __init__(self) -> None:
        """Initialize provider manager."""
        self._provider: BaseProvider | None = None

    def register(self, provider: BaseProvider) -> None:
        """Register active provider."""
        self._provider = provider

    @property
    def provider(self) -> BaseProvider | None:
        """Return active provider."""
        return self._provider

    @property
    def provider_name(self) -> str:
        """Return provider name."""
        if self._provider is None:
            return "None"

        return self._provider.name