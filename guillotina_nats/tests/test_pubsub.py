from guillotina.component import get_utility
from guillotina_nats.interfaces import INatsUtility

import asyncio
import pytest


@pytest.mark.asyncio
async def test_pubsub(natsd, container_requester):
    async with container_requester as requester:  # noqa
        nats = get_utility(INatsUtility)

        variable = []

        async def callback(msg):
            variable.append("done")

        await nats.subscribe(callback, "testing")
        await nats.publish("testing", b"hola")

        await asyncio.sleep(1)
        assert variable[0] == "done"
