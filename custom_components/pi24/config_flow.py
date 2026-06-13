# Copyright 2026 Lordseriouspig
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT

from .const import (
    CONF_FEED_TYPE,
    CONF_FILTER_RADIUS,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    DEFAULT_FEED_TYPE,
    DEFAULT_NAME,
    FEED_DUMP1090,
    FEED_FR24,
    DOMAIN,
)


def _build_schema(defaults: dict[str, object]) -> vol.Schema:
    """Build the user form schema."""

    return vol.Schema(
        {
            vol.Optional(CONF_NAME, default=defaults.get(CONF_NAME, DEFAULT_NAME)): str,
            vol.Required(CONF_HOST, default=defaults.get(CONF_HOST, "localhost")): str,
            vol.Required(CONF_PORT, default=defaults.get(CONF_PORT, 8754)): int,
            vol.Required(CONF_LATITUDE, default=defaults.get(CONF_LATITUDE, 0.0)): vol.Coerce(float),
            vol.Required(CONF_LONGITUDE, default=defaults.get(CONF_LONGITUDE, 0.0)): vol.Coerce(float),
            vol.Required(
                CONF_FEED_TYPE,
                default=defaults.get(CONF_FEED_TYPE, DEFAULT_FEED_TYPE),
            ): vol.In([FEED_FR24, FEED_DUMP1090]),
            vol.Optional(CONF_FILTER_RADIUS, default=defaults.get(CONF_FILTER_RADIUS, 0.0)): vol.Coerce(float),
        }
    )


class Pi24ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pi24."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            title = user_input.get(CONF_NAME) or f"Pi24 {user_input[CONF_HOST]}"
            return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=_build_schema({}),
        )


class Pi24OptionsFlow(config_entries.OptionsFlow):
    """Handle options for Pi24."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        defaults = {**self._config_entry.data, **self._config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=_build_schema(defaults),
        )


async def async_get_options_flow(config_entry: config_entries.ConfigEntry):
    """Return the options flow for this handler."""

    return Pi24OptionsFlow(config_entry)