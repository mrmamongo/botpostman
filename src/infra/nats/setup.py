import nats
from nats.aio.client import Client

from src.config import NatsConfig


async def setup_nats(config: NatsConfig) -> Client:
    nc = await nats.connect(config.nats_url)

    js = nc.jetstream()

    await js.add_stream(name="postman", subjects=["postman.dispatch"])

    return nc
