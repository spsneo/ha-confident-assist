"""Fixtures shared by every test. Nothing here calls a real API."""

from __future__ import annotations

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant.common import MockConfigEntry

from custom_components.confident_assist.const import (
    CONF_FALLBACK_AGENT,
    CONF_FALLBACK_PROVIDER,
    DOMAIN,
)

FALLBACK = "conversation.home_assistant"


@pytest.fixture(autouse=True)
async def homeassistant_component(hass: HomeAssistant) -> None:
    """A real instance always has these, and conversation reads them."""
    assert await async_setup_component(hass, "homeassistant", {})
    assert await async_setup_component(hass, "conversation", {})


@pytest.fixture
def entry(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Confident Assist",
        data={},
        options={CONF_FALLBACK_PROVIDER: "ha_agent", CONF_FALLBACK_AGENT: FALLBACK},
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
async def loaded(hass: HomeAssistant, entry: MockConfigEntry) -> MockConfigEntry:
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry
