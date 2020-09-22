from guillotina.component import get_utility
from guillotina_nats.interfaces import INatsUtility

import pytest


@pytest.mark.asyncio
async def test_connection(natsd, container_requester):
    async with container_requester as requester:  # noqa
        nats = get_utility(INatsUtility)

        assert nats._initialized
