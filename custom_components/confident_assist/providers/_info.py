"""Typed constructors for ProviderInfo, so each registry keeps its own type.

A decision_info twin arrives with the first decision provider.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import Any

import probatio as vol
from homeassistant.core import HomeAssistant

from .base import FallbackProvider, ProviderInfo


def fallback_info(
    key: str,
    schema: Callable[[HomeAssistant, Mapping[str, Any]], vol.Schema],
    create: Callable[[HomeAssistant, Mapping[str, Any]], Awaitable[FallbackProvider]],
) -> ProviderInfo[FallbackProvider]:
    return ProviderInfo(key, schema, create)
