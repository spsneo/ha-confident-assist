"""Fallback to any conversation agent installed in Home Assistant.

This covers every LLM that Home Assistant already has an integration for, such as
OpenAI, Anthropic, Google and Ollama, with no code of ours per LLM.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

import probatio as vol
from homeassistant.components import conversation
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import selector

from ...const import CONF_FALLBACK_AGENT, DOMAIN
from .._info import fallback_info

_LOGGER = logging.getLogger(__name__)


class HomeAssistantAgentFallback:
    """Hands the sentence to another conversation agent, in the same conversation."""

    def __init__(self, hass: HomeAssistant, agent_id: str | None) -> None:
        self._hass = hass
        self._agent_id = agent_id

    def _agent(self) -> str | None:
        """The agent to call, or None if there is none or it would loop.

        Another Confident Assist agent is a loop: two entries that fall back to
        each other pass the sentence between them and pay for each pass.
        """
        agent = self._agent_id
        if not agent:
            return None
        registered = er.async_get(self._hass).async_get(agent)
        entry = self._hass.config_entries.async_get_entry(agent)
        if (registered and registered.platform == DOMAIN) or (
            entry and entry.domain == DOMAIN
        ):
            _LOGGER.warning("Fallback agent %s is a Confident Assist agent", agent)
            return None
        return agent

    async def async_converse(
        self,
        user_input: conversation.ConversationInput,
        chat_log: conversation.ChatLog,
    ) -> conversation.ConversationResult | None:
        agent = self._agent()
        if agent is None:
            return None
        # The chat session's id, not the one the caller sent. A client that starts
        # a conversation sends None or an expired id, and the fallback agent would
        # then keep its memory under an id the client never hears.
        return await conversation.async_converse(
            self._hass,
            user_input.text,
            chat_log.conversation_id,
            user_input.context,
            language=user_input.language,
            agent_id=agent,
            device_id=user_input.device_id,
            satellite_id=user_input.satellite_id,
            extra_system_prompt=user_input.extra_system_prompt,
        )


def _schema(hass: HomeAssistant, options: Mapping[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(
                CONF_FALLBACK_AGENT,
                description={"suggested_value": options.get(CONF_FALLBACK_AGENT)},
            ): selector.ConversationAgentSelector(
                selector.ConversationAgentSelectorConfig()
            ),
        }
    )


async def _create(
    hass: HomeAssistant, options: Mapping[str, Any]
) -> HomeAssistantAgentFallback:
    return HomeAssistantAgentFallback(hass, options.get(CONF_FALLBACK_AGENT))


HA_AGENT = fallback_info("ha_agent", _schema, _create)
