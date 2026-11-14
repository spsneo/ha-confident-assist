"""Setting up and removing an entry."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant.common import MockConfigEntry


async def test_unload(hass: HomeAssistant, loaded: MockConfigEntry) -> None:
    assert loaded.state is ConfigEntryState.LOADED
    assert await hass.config_entries.async_unload(loaded.entry_id)
    assert loaded.state is ConfigEntryState.NOT_LOADED
