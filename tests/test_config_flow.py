"""The setup form and the options form."""

from __future__ import annotations

from unittest.mock import patch

from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant.common import MockConfigEntry

from custom_components.confident_assist.const import (
    CONF_FALLBACK_AGENT,
    CONF_FALLBACK_PROVIDER,
    DOMAIN,
)
from custom_components.confident_assist.providers.fallback.ha_agent import HA_AGENT

from .conftest import FALLBACK

# A second provider, so the forms that pick one are shown.
TWO_PROVIDERS = {"ha_agent": HA_AGENT, "other": HA_AGENT}
REGISTRY = "custom_components.confident_assist.config_flow.FALLBACK_PROVIDERS"


async def test_setup_with_one_provider_asks_only_for_the_agent(
    hass: HomeAssistant,
) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "fallback"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_FALLBACK_AGENT: FALLBACK}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Confident Assist"
    assert result["data"] == {}
    assert result["options"] == {
        CONF_FALLBACK_PROVIDER: "ha_agent",
        CONF_FALLBACK_AGENT: FALLBACK,
    }


async def test_setup_with_two_providers_asks_which_first(hass: HomeAssistant) -> None:
    with patch(REGISTRY, TWO_PROVIDERS):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
        assert result["step_id"] == "user"

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_FALLBACK_PROVIDER: "other"}
        )
        assert result["step_id"] == "fallback"

        result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["options"] == {CONF_FALLBACK_PROVIDER: "other"}


async def test_options_change_the_agent_and_reload(
    hass: HomeAssistant, loaded: MockConfigEntry
) -> None:
    result = await hass.config_entries.options.async_init(loaded.entry_id)
    assert result["step_id"] == "fallback"
    schema = result["data_schema"].schema
    shown = next(key for key in schema if key == CONF_FALLBACK_AGENT)
    assert shown.description == {"suggested_value": FALLBACK}

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_FALLBACK_AGENT: "conversation.other"}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert loaded.options == {
        CONF_FALLBACK_PROVIDER: "ha_agent",
        CONF_FALLBACK_AGENT: "conversation.other",
    }


async def test_options_switching_provider_starts_its_form_empty(
    hass: HomeAssistant, loaded: MockConfigEntry
) -> None:
    with patch(REGISTRY, TWO_PROVIDERS):
        result = await hass.config_entries.options.async_init(loaded.entry_id)
        assert result["step_id"] == "init"

        result = await hass.config_entries.options.async_configure(
            result["flow_id"], {CONF_FALLBACK_PROVIDER: "other"}
        )
        assert result["step_id"] == "fallback"
        schema = result["data_schema"].schema
        shown = next(key for key in schema if key == CONF_FALLBACK_AGENT)
        assert shown.description == {"suggested_value": None}
