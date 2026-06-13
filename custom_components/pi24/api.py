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

from aiohttp import ClientSession
from flightradar_client.dump1090_aircrafts import Dump1090AircraftsFeedAggregator
from flightradar_client.fr24feed_flights import FlightradarFlightsFeedAggregator

from .const import (
    CONF_FEED_TYPE,
    CONF_FILTER_RADIUS,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    DEFAULT_FEED_TYPE,
    FEED_DUMP1090,
    FEED_FR24,
)


class Pi24Client:
    """Create and refresh a Pi24 feed."""

    def __init__(self, websession: ClientSession, config: dict[str, object]) -> None:
        latitude = float(config[CONF_LATITUDE])
        longitude = float(config[CONF_LONGITUDE])
        filter_radius = config.get(CONF_FILTER_RADIUS)
        feed_type = str(config.get(CONF_FEED_TYPE, DEFAULT_FEED_TYPE))
        hostname = str(config.get("host", "localhost"))
        port = int(config.get("port", 8754 if feed_type == FEED_FR24 else 8888))
        url = config.get("url")

        coordinates = (latitude, longitude)
        common_kwargs = {
            "filter_radius": float(filter_radius) if filter_radius is not None else None,
            "url": str(url) if url else None,
            "hostname": hostname,
            "port": port,
        }
        if feed_type == FEED_DUMP1090:
            self._feed = Dump1090AircraftsFeedAggregator(coordinates, websession, **common_kwargs)
        else:
            self._feed = FlightradarFlightsFeedAggregator(coordinates, websession, **common_kwargs)

    async def async_update(self) -> dict[str, object]:
        """Fetch the latest feed data."""

        status, entries = await self._feed.update()
        return {"status": status, "entries": entries or {}}