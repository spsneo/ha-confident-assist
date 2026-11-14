"""The Assist agent hands every sentence to the fallback, for now."""

from __future__ import annotations

from homeassistant.components import conversation
from homeassistant.core import Context, HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import intent
from pytest_homeassistant.common import MockConfigEntry

from custom_components.confident_assist.const import (
    CONF_FALLBACK_AGENT,
    CONF_FALLBACK_PROVIDER,
    DOMAIN,
)

AGENT = "conversation.confident_assist"


def _reply(result: conversation.ConversationResult) -> str:
    return str(result.response.speech["plain"]["speech"])


async def test_the_agent_is_registered(
    hass: HomeAssistant, loaded: MockConfigEntry
) -> None:
    registered = er.async_get(hass).async_get(AGENT)
    assert registered is not None
    assert registered.platform == DOMAIN
    assert registered.unique_id == loaded.entry_id
    # The decision API reads any language, and Home Assistant's intents speak it.
    assert conversation.async_get_agent(hass, AGENT).supported_languages == "*"


class _Recorder(conversation.AbstractConversationAgent):
    """A fallback agent that records what it heard and answers one line."""

    def __init__(self) -> None:
        self.heard: list[conversation.ConversationInput] = []

    @property
    def supported_languages(self) -> list[str]:
        return ["en"]

    async def async_process(
        self, user_input: conversation.ConversationInput
    ) -> conversation.ConversationResult:
        self.heard.append(user_input)
        answer = intent.IntentResponse(language="en")
        answer.async_set_speech("From the fallback.")
        return conversation.ConversationResult(
            response=answer, conversation_id=user_input.conversation_id
        )


async def test_a_sentence_goes_to_the_fallback_agent_whole(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    recorder = _Recorder()
    other = MockConfigEntry(domain="test", data={})
    other.add_to_hass(hass)
    conversation.async_set_agent(hass, other, recorder)
    hass.config_entries.async_update_entry(
        entry,
        options={CONF_FALLBACK_PROVIDER: "ha_agent", CONF_FALLBACK_AGENT: other.entry_id},
    )
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await conversation.async_converse(
        hass, "turn on the kitchen light", None, Context(), agent_id=AGENT
    )

    assert _reply(result) == "From the fallback."
    assert [heard.text for heard in recorder.heard] == ["turn on the kitchen light"]
    # The fallback joins this conversation, and the reply continues it.
    assert recorder.heard[0].conversation_id == result.conversation_id
    assert result.conversation_id is not None


async def test_the_default_agent_really_answers_as_fallback(
    hass: HomeAssistant, loaded: MockConfigEntry
) -> None:
    result = await conversation.async_converse(
        hass, "this matches no sentence at all", None, Context(), agent_id=AGENT
    )
    assert result.response.response_type is intent.IntentResponseType.ERROR


async def test_no_fallback_agent_says_it_did_not_understand(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.config_entries.async_update_entry(
        entry, options={CONF_FALLBACK_PROVIDER: "ha_agent"}
    )
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await conversation.async_converse(
        hass, "turn on the kitchen light", None, Context(), agent_id=AGENT
    )
    assert result.response.error_code is intent.IntentResponseErrorCode.NO_INTENT_MATCH
    assert _reply(result) == "Sorry, I did not understand that."


async def test_a_fallback_to_itself_is_refused(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    hass.config_entries.async_update_entry(
        entry, options={CONF_FALLBACK_PROVIDER: "ha_agent", CONF_FALLBACK_AGENT: AGENT}
    )
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await conversation.async_converse(
        hass, "turn on the kitchen light", None, Context(), agent_id=AGENT
    )
    assert _reply(result) == "Sorry, I did not understand that."


async def test_a_fallback_to_another_entry_is_refused(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    other = MockConfigEntry(domain=DOMAIN, data={}, options={})
    other.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        entry,
        options={CONF_FALLBACK_PROVIDER: "ha_agent", CONF_FALLBACK_AGENT: other.entry_id},
    )
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await conversation.async_converse(
        hass, "turn on the kitchen light", None, Context(), agent_id=AGENT
    )
    assert _reply(result) == "Sorry, I did not understand that."
