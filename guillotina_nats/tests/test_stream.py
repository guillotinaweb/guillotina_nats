from guillotina.component import get_utility
from guillotina_nats.interfaces import INatsUtility

import asyncio
import pytest


@pytest.mark.asyncio
@pytest.mark.app_settings(
    {"load_utilities": {"nats": {"settings": {"stan": "test-cluster"}}}}
)
async def test_stream(stand, container_requester):
    async with container_requester as requester:  # noqa
        nats = get_utility(INatsUtility)

        variable = []

        await nats.stream("testingst", b"hola")

        async def callback(msg):
            variable.append("done")

        await nats.stream_subscribe(callback, "testingst", start_at="first")

        await asyncio.sleep(1)

        assert variable[0] == "done"
