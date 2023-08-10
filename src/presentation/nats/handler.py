import logging
from typing import Callable

import ormsgpack
from aiogram import Bot
from nats.aio.client import Client
from nats.aio.msg import Msg

from src.application.postman.dto import DispatchMessage
from src.application.subscribers.interfaces import SubscriberRepo
from src.presentation.nats.collections import State

MessageHandler = Callable


class NatsHandler:
    def __init__(self, nats: Client) -> None:
        self.nats = nats
        self.logger = logging.getLogger(self.__class__.__name__)
        self.state = State()

    async def setup(self) -> None:
        js = self.nats.jetstream()

        await js.subscribe("postman.dispatch", cb=self.handle_dispatch)

    async def handle_dispatch(self, msg_raw: Msg) -> None:
        msg = DispatchMessage.parse_obj(ormsgpack.unpackb(msg_raw.data))

        async with self.state.sub_repo() as repo:  # type: SubscriberRepo
            subs = await repo.get_all()

        bot: Bot = self.state.bot()
        for sub in subs:
            await bot.send_message(
                chat_id=sub.telegram_id, text=f"{msg.from_username} - {msg.message}"
            )
