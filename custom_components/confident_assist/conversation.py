"""The Assist agent.

For now every sentence goes to the fallback provider. The decision step, which
acts on a sentence only when the decision API is sure, comes with the core logic.
"""

from __future__ import annotations

from typing import Literal

from homeassistant.components import conversation
from homeassistant.const import MATCH_ALL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import intent, translation
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import ConfidentAssistConfigEntry
from .const import DOMAIN

PARALLEL_UPDATES = 0

# Used when a translation is missing, so the reply is still a sentence.
_NOT_UNDERSTOOD = "Sorry, I did not understand that."


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfidentAssistConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    async_add_entities([ConfidentAssistEntity(entry)])


class ConfidentAssistEntity(conversation.ConversationEntity):
    """Answers one sentence: act when sure, else hand it to the fallback."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = conversation.ConversationEntityFeature.CONTROL

    def __init__(self, entry: ConfidentAssistConfigEntry) -> None:
        self._entry = entry
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def supported_languages(self) -> list[str] | Literal["*"]:
        return MATCH_ALL

    async def _async_handle_message(
        self,
        user_input: conversation.ConversationInput,
        chat_log: conversation.ChatLog,
    ) -> conversation.ConversationResult:
        result = await self._entry.runtime_data.fallback.async_converse(
            user_input, chat_log
        )
        if result is None:
            result = await self._not_understood(user_input)
        # The chat session's id continues the conversation; the caller's may not.
        result.conversation_id = chat_log.conversation_id
        return result

    async def _not_understood(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        key = f"component.{DOMAIN}.common.not_understood"
        lines = await translation.async_get_translations(
            self.hass, user_input.language, "common", [DOMAIN]
        )
        response = intent.IntentResponse(language=user_input.language)
        response.async_set_error(
            intent.IntentResponseErrorCode.NO_INTENT_MATCH,
            lines.get(key, _NOT_UNDERSTOOD),
        )
        return conversation.ConversationResult(response=response)
