"""The two provider interfaces, and how a provider describes itself."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol

import probatio as vol
from homeassistant.components import conversation
from homeassistant.core import HomeAssistant

from .types import Decision, Question


class DecisionProvider(Protocol):
    """Reads one sentence and answers typed questions about it."""

    async def ask(
        self, state: Mapping[str, Any], questions: Mapping[str, Question]
    ) -> Decision:
        """Answer every question in one request."""

    def estimate_tokens(
        self, state: Mapping[str, Any], questions: Mapping[str, Question]
    ) -> int:
        """The input tokens a request will cost, for the daily budget."""

    async def async_validate(self) -> None:
        """Raise ProviderAuthError or ProviderUnavailableError if setup cannot work."""


class FallbackProvider(Protocol):
    """Takes the whole sentence when the agent is not sure what it means."""

    async def async_converse(
        self,
        user_input: conversation.ConversationInput,
        chat_log: conversation.ChatLog,
    ) -> conversation.ConversationResult | None:
        """Answer the sentence, or None when there is nobody to hand it to."""


@dataclass(frozen=True, slots=True)
class ProviderInfo[P]:
    """What the config flow shows for a provider, and how to build one.

    `schema` builds the provider's form from the options it already has, so the
    same form serves setup and the options flow. `create` builds a working
    provider from those options.
    """

    key: str
    schema: Callable[[HomeAssistant, Mapping[str, Any]], vol.Schema]
    create: Callable[[HomeAssistant, Mapping[str, Any]], Awaitable[P]]
