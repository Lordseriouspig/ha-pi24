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

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, UPDATE_ERROR

_LOGGER = logging.getLogger(__name__)


class Pi24Coordinator(DataUpdateCoordinator[dict[str, object]]):
    """Coordinate a single Pi24 instance."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        client,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}-{config_entry.entry_id}",
            update_interval=timedelta(seconds=15),
        )
        self.config_entry = config_entry
        self.client = client
        self.total_aircraft_entries = 0
        self.seen_aircraft_ids: set[str] = set()
        self._previous_active_aircraft_ids: set[str] = set()

    @property
    def cumulative_aircraft_count(self) -> int:
        """Return the total number of airspace entries during this coordinator lifetime."""

        return self.total_aircraft_entries

    @property
    def unique_aircraft_count(self) -> int:
        """Return the number of unique aircraft seen during this coordinator lifetime."""

        return len(self.seen_aircraft_ids)

    async def _async_update_data(self) -> dict[str, object]:
        data = await self.client.async_update()
        if data["status"] == UPDATE_ERROR:
            raise UpdateFailed("Unable to fetch Pi24 data")

        entries = data.get("entries") or {}
        current_aircraft_ids: set[str] = set()
        for entry in entries.values():
            external_id = getattr(entry, "external_id", None)
            if external_id:
                current_aircraft_ids.add(external_id)

        entered_aircraft_ids = current_aircraft_ids.difference(
            self._previous_active_aircraft_ids
        )
        self.total_aircraft_entries += len(entered_aircraft_ids)
        for external_id in entered_aircraft_ids:
            if external_id:
                self.seen_aircraft_ids.add(external_id)

        self._previous_active_aircraft_ids = current_aircraft_ids

        return data