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

from typing import Any, cast

from homeassistant.components.geo_location import GeolocationEvent
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN
from .coordinator import Pi24Coordinator

ATTR_EXTERNAL_ID = "external_id"


def _active_aircraft_entries(data: dict[str, object]) -> dict[str, object]:
    """Return only aircraft entries with valid coordinates."""

    entries = data.get("entries") or {}
    active: dict[str, object] = {}
    for external_id, entry in entries.items():
        coordinates = getattr(entry, "coordinates", None)
        if coordinates and coordinates != (None, None):
            active[str(external_id)] = entry
    return active


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Pi24 geolocation entities from a config entry."""

    coordinator = cast(Pi24Coordinator, hass.data[DOMAIN][entry.entry_id])
    entities: dict[str, Pi24AircraftLocationEvent] = {}

    @callback
    def _async_handle_coordinator_update() -> None:
        data = coordinator.data or {}
        aircraft_entries = _active_aircraft_entries(data)

        active_ids = set(aircraft_entries)
        known_ids = set(entities)

        removed_ids = known_ids - active_ids
        for external_id in removed_ids:
            entity = entities[external_id]
            entity._attr_available = False
            entity.async_write_ha_state()

        new_entities: list[Pi24AircraftLocationEvent] = []
        added_ids = active_ids - known_ids
        for external_id in added_ids:
            entity = Pi24AircraftLocationEvent(
                entry.entry_id,
                external_id,
                aircraft_entries[external_id],
            )
            entities[external_id] = entity
            new_entities.append(entity)

        if new_entities:
            async_add_entities(new_entities)

        updated_ids = active_ids & known_ids
        for external_id in updated_ids:
            entity = entities[external_id]
            entity.update_from_feed(aircraft_entries[external_id])
            entity.async_write_ha_state()

    remove_listener = coordinator.async_add_listener(_async_handle_coordinator_update)
    entry.async_on_unload(remove_listener)
    _async_handle_coordinator_update()


class Pi24AircraftLocationEvent(GeolocationEvent):
    """Representation of a single active aircraft on the map."""

    _attr_icon = "mdi:airplane"
    _attr_should_poll = False
    _attr_source = DOMAIN
    _attr_unit_of_measurement = UnitOfLength.KILOMETERS

    def __init__(self, entry_id: str, external_id: str, feed_entry: object) -> None:
        """Initialize a geolocation event from a feed entry."""

        self._external_id = external_id
        self._attr_unique_id = f"{entry_id}_{external_id}"

        self._callsign: str | None = None
        self._altitude: int | None = None
        self._speed: int | None = None
        self._track: int | None = None
        self._squawk: str | None = None
        self._vert_rate: int | None = None
        self._updated: str | None = None

        self.update_from_feed(feed_entry)

    def update_from_feed(self, feed_entry: object) -> None:
        """Update entity values from a feed entry."""

        coordinates = getattr(feed_entry, "coordinates", None) or (None, None)

        self._attr_name = getattr(feed_entry, "callsign", None) or self._external_id
        self._attr_distance = round(getattr(feed_entry, "distance_to_home", 0), 1)
        self._attr_latitude = coordinates[0]
        self._attr_longitude = coordinates[1]

        self._callsign = getattr(feed_entry, "callsign", None)
        self._altitude = getattr(feed_entry, "altitude", None)
        self._speed = getattr(feed_entry, "speed", None)
        self._track = getattr(feed_entry, "track", None)
        self._squawk = getattr(feed_entry, "squawk", None)
        self._vert_rate = getattr(feed_entry, "vert_rate", None)

        updated = getattr(feed_entry, "updated", None)
        self._updated = updated.isoformat() if updated else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes for this aircraft."""

        return {
            key: value
            for key, value in (
                (ATTR_EXTERNAL_ID, self._external_id),
                ("callsign", self._callsign),
                ("altitude", self._altitude),
                ("speed", self._speed),
                ("track", self._track),
                ("squawk", self._squawk),
                ("vertical_rate", self._vert_rate),
                ("updated", self._updated),
            )
            if value is not None
        }
