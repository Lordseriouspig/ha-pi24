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
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, cast

from homeassistant.components.sensor import (
	SensorDeviceClass,
	SensorEntity,
	SensorEntityDescription,
	SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import Pi24Coordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class Pi24SensorEntityDescription(SensorEntityDescription):
	"""Describe a Pi24 sensor."""

	value_fn: Callable[[dict[str, object]], object | None]


def _entries(data: dict[str, object]) -> list:
	entries = data.get("entries") or {}
	return list(entries.values())


def _nearest_entry(data: dict[str, object]):
	candidates = [entry for entry in _entries(data) if getattr(entry, "coordinates", None)]
	if not candidates:
		return None
	return min(candidates, key=lambda entry: entry.distance_to_home)


def _furthest_entry(data: dict[str, object]):
	candidates = [entry for entry in _entries(data) if getattr(entry, "coordinates", None)]
	if not candidates:
		return None
	return max(candidates, key=lambda entry: entry.distance_to_home)


def _serialize_datetime(value: datetime | None) -> str | None:
	"""Return an ISO formatted datetime string for entity attributes."""

	if value is None:
		return None
	return value.isoformat()


def _aircraft_summary(entry) -> dict[str, object | None]:
	"""Build a compact summary for one aircraft entry."""

	return {
		"id": entry.external_id,
		"callsign": entry.callsign,
		"altitude": entry.altitude,
		"speed": entry.speed,
		"track": entry.track,
		"squawk": entry.squawk,
		"distance_km": round(entry.distance_to_home, 1) if entry.coordinates else None,
		"coordinates": entry.coordinates,
		"updated": _serialize_datetime(entry.updated),
	}


def _entry_summary(entry) -> dict[str, object | None]:
	"""Build a shared aircraft summary for state attributes."""

	return _aircraft_summary(entry)


SENSOR_DESCRIPTIONS: tuple[Pi24SensorEntityDescription, ...] = (
	Pi24SensorEntityDescription(
		key="status",
		name="Status",
		icon="mdi:radar",
		value_fn=lambda data: data.get("status"),
	),
	Pi24SensorEntityDescription(
		key="aircraft_count",
		name="Aircraft Count",
		icon="mdi:airplane",
		state_class=SensorStateClass.MEASUREMENT,
		value_fn=lambda data: len(_entries(data)),
	),
	Pi24SensorEntityDescription(
		key="cumulative_aircraft_count",
		name="Cumulative Aircraft Entries",
		icon="mdi:counter",
		state_class=SensorStateClass.MEASUREMENT,
		value_fn=lambda data: 0,
	),
	Pi24SensorEntityDescription(
		key="unique_aircraft_count",
		name="Unique Aircraft Count",
		icon="mdi:counter",
		state_class=SensorStateClass.MEASUREMENT,
		value_fn=lambda data: 0,
	),
	Pi24SensorEntityDescription(
		key="nearest_aircraft",
		name="Nearest Aircraft",
		icon="mdi:crosshairs-gps",
		value_fn=lambda data: getattr(_nearest_entry(data), "callsign", None)
		or getattr(_nearest_entry(data), "external_id", None),
	),
	Pi24SensorEntityDescription(
		key="nearest_distance",
		name="Nearest Distance",
		icon="mdi:map-marker-distance",
		native_unit_of_measurement=UnitOfLength.KILOMETERS,
		state_class=SensorStateClass.MEASUREMENT,
		value_fn=lambda data: round(_nearest_entry(data).distance_to_home, 1)
		if _nearest_entry(data)
		else None,
	),
	Pi24SensorEntityDescription(
		key="furthest_aircraft",
		name="Furthest Aircraft",
		icon="mdi:crosshairs-gps",
		value_fn=lambda data: getattr(_furthest_entry(data), "callsign", None)
		or getattr(_furthest_entry(data), "external_id", None),
	),
	Pi24SensorEntityDescription(
		key="furthest_distance",
		name="Furthest Distance",
		icon="mdi:map-marker-distance",
		native_unit_of_measurement=UnitOfLength.KILOMETERS,
		state_class=SensorStateClass.MEASUREMENT,
		value_fn=lambda data: round(_furthest_entry(data).distance_to_home, 1)
		if _furthest_entry(data)
		else None,
	),
	Pi24SensorEntityDescription(
		key="latest_update",
		name="Latest Update",
		device_class=SensorDeviceClass.TIMESTAMP,
		value_fn=lambda data: max(
			(entry.updated for entry in _entries(data) if entry.updated),
			default=None,
		),
	),
)


async def async_setup_entry(
	hass: HomeAssistant,
	entry: ConfigEntry,
	async_add_entities: AddEntitiesCallback,
) -> None:
	"""Set up Pi24 sensors from a config entry."""

	coordinator = cast(Pi24Coordinator, hass.data[DOMAIN][entry.entry_id])
	async_add_entities(Pi24Sensor(coordinator, description) for description in SENSOR_DESCRIPTIONS)


class Pi24Sensor(CoordinatorEntity[Pi24Coordinator], SensorEntity):
	"""Representation of a Pi24 summary sensor."""

	entity_description: Pi24SensorEntityDescription

	def __init__(
		self,
		coordinator: Pi24Coordinator,
		description: Pi24SensorEntityDescription,
	) -> None:
		super().__init__(coordinator)
		self.entity_description = description
		self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"
		self._attr_has_entity_name = True
		self._attr_name = description.name

	@property
	def native_value(self):
		"""Return the current sensor value."""

		if self.entity_description.key == "cumulative_aircraft_count":
			return self.coordinator.cumulative_aircraft_count
		if self.entity_description.key == "unique_aircraft_count":
			return self.coordinator.unique_aircraft_count

		data = self.coordinator.data or {}
		return self.entity_description.value_fn(data)

	@property
	def extra_state_attributes(self):
		"""Expose a few useful feed attributes."""

		data = self.coordinator.data or {}
		if self.entity_description.key == "aircraft_count":
			entries = _entries(data)
			return {
				"aircraft": [_entry_summary(entry) for entry in entries],
				"aircraft_ids": [entry.external_id for entry in entries],
			}

		if self.entity_description.key == "cumulative_aircraft_count":
			return {
				"total_aircraft_entries": self.coordinator.total_aircraft_entries,
			}

		if self.entity_description.key == "unique_aircraft_count":
			return {
				"seen_aircraft_ids": sorted(self.coordinator.seen_aircraft_ids),
			}

		if self.entity_description.key in {"furthest_aircraft", "furthest_distance"}:
			selected = _furthest_entry(data)
		else:
			selected = _nearest_entry(data)

		nearest = selected
		if nearest is None:
			return {}

		return {
			"callsign": nearest.callsign,
			"altitude": nearest.altitude,
			"speed": nearest.speed,
			"track": nearest.track,
			"squawk": nearest.squawk,
			"updated": _serialize_datetime(nearest.updated),
		}

	@property
	def device_info(self):
		"""Return device information for the Pi24 receiver."""

		entry = self.coordinator.config_entry
		return DeviceInfo(
			identifiers={(DOMAIN, entry.entry_id)},
			name=entry.title,
			manufacturer="Flightradar24",
			model=str(entry.data.get("feed_type", "pi24")),
		)

