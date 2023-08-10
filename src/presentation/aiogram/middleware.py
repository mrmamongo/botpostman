from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message
from nats.aio.client import Client

from src.application.postman.service import PostmanService
from src.infra.database.repositories import DatabaseSubscriberRepo


class NatsMiddleware(BaseMiddleware):
    def __init__(self, nats: Client) -> None:
        self.nats = nats

    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any],
    ) -> Any:
        js = self.nats.jetstream()
        data["jetstream"] = js
        return await handler(event, data)


class PostmanMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any],
    ) -> Any:
        js = data["jetstream"]
        data["postman"] = PostmanService(js)
        return await handler(event, data)


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, smaker: Any) -> None:
        self.session = smaker

    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any],
    ) -> Any:
        async with self.session() as session:
            data["db_session"] = session
            return await handler(event, data)


class SubscriberRepoMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: dict[str, Any],
    ) -> Any:
        db_session = data["db_session"]
        data["sub_repo"] = DatabaseSubscriberRepo(db_session)
        return await handler(event, data)
