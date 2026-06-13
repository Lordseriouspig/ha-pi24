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

from typing import Final

DOMAIN: Final = "pi24"
NAME: Final = "Pi24 Monitor"
DEFAULT_NAME: Final = NAME

CONF_FEED_TYPE: Final = "feed_type"
CONF_FILTER_RADIUS: Final = "filter_radius"
CONF_LATITUDE: Final = "latitude"
CONF_LONGITUDE: Final = "longitude"

FEED_FR24: Final = "fr24feed"
FEED_DUMP1090: Final = "dump1090"
DEFAULT_FEED_TYPE: Final = FEED_FR24

ATTR_ALTITUDE = "altitude"
ATTR_CALLSIGN = "callsign"
ATTR_FLIGHT = "flight"
ATTR_HEX = "hex"
ATTR_LAT = "lat"
ATTR_LATITUDE = "latitude"
ATTR_LON = "lon"
ATTR_LONGITUDE = "longitude"
ATTR_MODE_S = "mode_s"
ATTR_SPEED = "speed"
ATTR_SQUAWK = "squawk"
ATTR_TRACK = "track"
ATTR_UPDATED = "updated"
ATTR_VERT_RATE = "vert_rate"

UPDATE_OK = "OK"
UPDATE_ERROR = "ERROR"