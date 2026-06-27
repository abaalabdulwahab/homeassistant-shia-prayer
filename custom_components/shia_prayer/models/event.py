"""Religious event model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReligiousEvent:
    """Religious event."""

    title: str
    description: str
    date: str
    source: str