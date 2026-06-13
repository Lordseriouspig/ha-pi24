<!--
 Copyright 2026 Lordseriouspig
 
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
 
     https://www.apache.org/licenses/LICENSE-2.0
 
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
-->

# Pi24 Monitor

Home Assistant custom integration for monitoring Pi24 ADS-B receivers through the `flightradar-client` Python library.

## What it provides

- Receiver status sensor
- Active aircraft count sensor
- Nearest aircraft sensor
- Nearest distance sensor
- Latest update timestamp sensor

## Setup

1. Install the integration through HACS or copy `custom_components/pi24` into your Home Assistant config.
2. Add a new Pi24 instance from the Home Assistant integrations page.
3. Enter the receiver host, port, receiver coordinates, and feed type.

The integration supports both `fr24feed` and `dump1090` feeds.

