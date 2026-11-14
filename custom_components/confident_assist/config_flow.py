"""Set up Confident Assist from the UI.

Every setting lives in the entry's options, so setup and the options flow share
one form per provider.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import probatio as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import CONF_FALLBACK_PROVIDER, DOMAIN
from .providers import FALLBACK_PROVIDERS


def _provider_schema(current: str) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_FALLBACK_PROVIDER, default=current
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=list(FALLBACK_PROVIDERS),
                    translation_key=CONF_FALLBACK_PROVIDER,
                    mode=selector.SelectSelectorMode.LIST,
                )
            )
        }
    )


class ConfidentAssistConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._provider = next(iter(FALLBACK_PROVIDERS))

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Pick the fallback provider. Skipped while there is only one."""
        if user_input is not None:
            self._provider = user_input[CONF_FALLBACK_PROVIDER]
            return await self.async_step_fallback()
        if len(FALLBACK_PROVIDERS) == 1:
            return await self.async_step_fallback()
        return self.async_show_form(
            step_id="user", data_schema=_provider_schema(self._provider)
        )

    async def async_step_fallback(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        info = FALLBACK_PROVIDERS[self._provider]
        if user_input is not None:
            return self.async_create_entry(
                title="Confident Assist",
                data={},
                options={CONF_FALLBACK_PROVIDER: self._provider, **user_input},
            )
        return self.async_show_form(
            step_id="fallback", data_schema=info.schema(self.hass, {})
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return ConfidentAssistOptionsFlow()


class ConfidentAssistOptionsFlow(OptionsFlow):
    def __init__(self) -> None:
        self._provider: str | None = None

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        current = self.config_entry.options.get(
            CONF_FALLBACK_PROVIDER, next(iter(FALLBACK_PROVIDERS))
        )
        if user_input is not None:
            self._provider = user_input[CONF_FALLBACK_PROVIDER]
            return await self.async_step_fallback()
        if len(FALLBACK_PROVIDERS) == 1:
            self._provider = current
            return await self.async_step_fallback()
        return self.async_show_form(step_id="init", data_schema=_provider_schema(current))

    async def async_step_fallback(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        assert self._provider is not None
        info = FALLBACK_PROVIDERS[self._provider]
        if user_input is not None:
            return self.async_create_entry(
                data={CONF_FALLBACK_PROVIDER: self._provider, **user_input}
            )
        # A provider's options only carry over when the provider stays the same.
        previous: Mapping[str, Any] = self.config_entry.options
        if previous.get(CONF_FALLBACK_PROVIDER) != self._provider:
            previous = {}
        return self.async_show_form(
            step_id="fallback", data_schema=info.schema(self.hass, previous)
        )
