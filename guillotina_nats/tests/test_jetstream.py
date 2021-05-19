from guillotina.component import get_utility
from guillotina_nats.interfaces import INatsUtility
from guillotina_nats.models import ConsumerConfig
from guillotina_nats.models import DeliverPolicy
from guillotina_nats.models import StreamConfig
from nats.aio.errors import ErrTimeout

import pytest


@pytest.mark.asyncio
async def test_js_stream(natsd, container_requester):
    async with container_requester as requester:  # noqa
        nats = get_utility(INatsUtility)

        res = await nats.js_info()
        assert res["consumers"] == 0

        res = await nats.js_streams()
        assert len(res["streams"]) == 0

        config = StreamConfig(name="ORDERS")
        config.subjects.append("ORDERS.*")
        res = await nats.js_stream_create(config)
        assert res["type"] == "io.nats.jetstream.api.v1.stream_create_response"
        assert "error" not in res

        config = ConsumerConfig()
        config.filter_subject = "ORDERS.processed"
        config.sample_freq = "0"
        config.deliver_policy = DeliverPolicy.new
        config.max_deliver = 10
        config.ack_wait = int(3e10)
        config.max_ack_pending = 1
        config.durable_name = "DISPATCH"
        res = await nats.js_consumer_durable_create("ORDERS", config)
        assert res["type"] == "io.nats.jetstream.api.v1.consumer_create_response"
        assert "error" not in res

        res = await nats.js_consumer_list("ORDERS")
        assert res["total"] == 1
        assert res["consumers"][0]["name"] == "DISPATCH"

        res = await nats.js_consumer_info("ORDERS", "DISPATCH")
        assert res["num_pending"] == 0

        config = ConsumerConfig()
        config.filter_subject = "ORDERS.sent"
        config.durable_name = "SENT"
        res = await nats.js_consumer_durable_create("ORDERS", config)
        assert res["type"] == "io.nats.jetstream.api.v1.consumer_create_response"
        assert "error" not in res

        await nats.publish("ORDERS.sent", b"Hola")
        await nats.publish("ORDERS.processed", b"Adeu")
        await nats.publish("ORDERS.sent", b"Hola de nou")
        await nats.publish("ORDERS.processed", b"Hola de nou")

        body = await nats.js_get_next("ORDERS", "DISPATCH")
        assert body.data == b"Adeu"
        await nats.js_consumer_ack(body.reply)

        body = await nats.js_get_next("ORDERS", "SENT")
        assert body.data == b"Hola"
        await nats.js_consumer_ack(body.reply)

        body = await nats.js_get_next("ORDERS", "DISPATCH")
        assert body.data == b"Hola de nou"
        body = await nats.js_get_next("ORDERS", "SENT")
        assert body.data == b"Hola de nou"

        with pytest.raises(ErrTimeout):
            body = await nats.js_get_next("ORDERS", "DISPATCH")

        message = await nats.js_get_message("ORDERS", 1)
        assert message == b"Hola"
        message2 = await nats.js_get_message("ORDERS", 2)
        assert message2 == b"Adeu"
        message3 = await nats.js_get_message("ORDERS", 3)
        assert message3 == b"Hola de nou"
        message4 = await nats.js_get_message("ORDERS", 5)
        assert message4 is None
