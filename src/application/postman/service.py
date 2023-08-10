import ormsgpack
from nats.aio.client import Client
from nats.js import JetStreamContext

from src.application.postman.dto import DispatchMessage


class PostmanService:
    def __init__(self, js: JetStreamContext):
        self.js = js

    async def perform_dispatch(self, message: DispatchMessage) -> None:
        await self.js.publish(
            subject="postman.dispatch",
            payload=ormsgpack.packb(message.dict()),
        )
