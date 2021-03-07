# Copyright 2019-2021 Patrick Dreker <patrick@dreker.de>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import logging
import os
import sys

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY

from fritzexporter.fritzdevice import FritzCollector, FritzDevice

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)


def main():
    fritzcollector = FritzCollector()

    if 'FRITZ_EXPORTER_CONFIG' in os.environ:
        fritz_config_env = os.getenv('FRITZ_EXPORTER_CONFIG')
        fritz_config = [x.strip() for x in fritz_config_env.split(',')]
        configs = int(len(fritz_config) / 3)
        for device in range(configs):
            address = fritz_config.pop(0)
            username = fritz_config.pop(0)
            password = fritz_config.pop(0)
            fritzcollector.register(FritzDevice(address, username, password))
    elif 'FRITZ_HOSTNAME' and 'FRITZ_USERNAME' and 'FRITZ_PASSWORD' in os.environ:
        address = os.getenv('FRITZ_HOSTNAME')
        username = os.getenv('FRITZ_USERNAME')
        password = os.getenv('FRITZ_PASSWORD')
        fritzcollector.register(FritzDevice(address, username, password))
    else:
        logger.critical('no ENV variables set. Exiting.')
        sys.exit(1)

    REGISTRY.register(fritzcollector)

    port = os.getenv('FRITZ_EXPORTER_PORT', 9787)
    logger.info(f'Starting listener at {port}')
    start_http_server(int(port))

    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    finally:
        loop.close()


if __name__ == '__main__':
    main()
