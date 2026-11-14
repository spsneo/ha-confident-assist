"""Decision and fallback providers.

A provider is one module that declares a ProviderInfo. The config flow and the
agent read the registries below, so a new provider needs no change anywhere else.
"""

from __future__ import annotations

from .base import DecisionProvider, FallbackProvider, ProviderInfo
from .fallback.ha_agent import HA_AGENT

# Decision providers read the sentence and give typed answers with a confidence.
# The first one, Jev, arrives with the core logic.
DECISION_PROVIDERS: dict[str, ProviderInfo[DecisionProvider]] = {}

# Fallback providers get the whole sentence when the agent is not sure.
FALLBACK_PROVIDERS: dict[str, ProviderInfo[FallbackProvider]] = {
    HA_AGENT.key: HA_AGENT,
}

__all__ = [
    "DECISION_PROVIDERS",
    "FALLBACK_PROVIDERS",
    "DecisionProvider",
    "FallbackProvider",
    "ProviderInfo",
]
