"""Confident Assist: an Assist agent that acts only when it is sure."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_FALLBACK_PROVIDER
from .providers import FALLBACK_PROVIDERS, FallbackProvider
from .providers.fallback.ha_agent import HA_AGENT

PLATFORMS = [Platform.CONVERSATION]


@dataclass(slots=True)
class RuntimeData:
    fallback: FallbackProvider


type ConfidentAssistConfigEntry = ConfigEntry[RuntimeData]


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfidentAssistConfigEntry
) -> bool:
    info = FALLBACK_PROVIDERS[entry.options.get(CONF_FALLBACK_PROVIDER, HA_AGENT.key)]
    entry.runtime_data = RuntimeData(fallback=await info.create(hass, entry.options))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: ConfidentAssistConfigEntry
) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload(hass: HomeAssistant, entry: ConfidentAssistConfigEntry) -> None:
    """New options mean a new provider, so the entry starts again."""
    await hass.config_entries.async_reload(entry.entry_id)
