"""
Server app config
"""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from nats.aio.client import Client
from sqlalchemy.ext.asyncio import AsyncEngine

from src.application.subscribers.interfaces import SubscriberRepo
from src.config import Config
from src.exceptions import DisposeException, StartupException
from src.infra.database.repositories import DatabaseSubscriberRepo
from src.infra.database.setup import setup_database
from src.infra.logging import setup_logging
from src.infra.nats.setup import setup_nats
from src.presentation.aiogram.middleware import NatsMiddleware, PostmanMiddleware, DatabaseMiddleware, \
    SubscriberRepoMiddleware
from src.presentation.aiogram.setup import setup_aiogram
from src.presentation.nats.handler import NatsHandler

logger = logging.getLogger(__name__)


class Application:
    def __init__(
        self,
        config: Config,
        bot: Bot,
        dp: Dispatcher,
        engine: AsyncEngine,
        nc: Client,
        handler: NatsHandler,
    ) -> None:
        self.config = config
        self.bot = bot
        self.dp = dp
        self.engine = engine
        self.nats = nc
        self.nats_handler = handler

    @classmethod
    async def from_config(cls, config: Config) -> Application:  # a.k.a startup
        setup_logging(config.logging)

        logger.info("Initializing database")
        sessionmaker, engine = setup_database(config.database)

        logger.info("Initializing nats")
        nc = await setup_nats(config.nats)

        logger.info("Initializing Telegram Bot")
        bot = Bot(token=config.telegram.token, parse_mode="HTML")
        dp = Dispatcher()

        logger.info("Initializing telegram bot dependencies")
        setup_aiogram(dp)

        dp.update.middleware(NatsMiddleware(nc))
        dp.update.middleware(PostmanMiddleware())
        dp.update.middleware(DatabaseMiddleware(sessionmaker))
        dp.update.middleware(SubscriberRepoMiddleware())

        logger.info("Initializing nats dependencies")
        handler = NatsHandler(nc)
        handler.state.bot = lambda: bot

        async def sub_repo() -> SubscriberRepo:
            async with sessionmaker() as session:
                yield DatabaseSubscriberRepo(session)

        handler.state.sub_repo = asynccontextmanager(sub_repo)

        logger.info("Initializing middlewares")
        # Add Auth middleware

        logger.info("Creating application")
        application = Application(
            config=config, bot=bot, dp=dp, engine=engine, nc=nc, handler=handler
        )

        logger.info("Initializing application finished")

        logger.info(f"Cprocessing config - {config.dict()}")

        return application

    async def start(self) -> None:
        logger.info("HTTP server is starting")

        try:
            await self.nats_handler.setup()
            await self.dp.start_polling(self.bot)
        except asyncio.CancelledError:
            logger.info("HTTP server has been interrupted")
        except BaseException as unexpected_error:
            logger.exception("HTTP server failed to start")

            raise StartupException from unexpected_error

    async def dispose(self) -> None:
        logger.info("Application is shutting down...")

        dispose_errors: list[str] = []

        try:
            await self.engine.dispose()
        except Exception as e:
            dispose_errors.append(repr(e))

        try:
            await self.nats.close()
        except Exception as e:
            dispose_errors.append(repr(e))

        try:
            await self.bot.delete_webhook(drop_pending_updates=True)
            await self.bot.close()
        except Exception as e:
            dispose_errors.append(repr(e))

        if len(dispose_errors) != 0:
            logger.error("Application has shut down with errors")
            raise DisposeException(
                "Application has shut down with errors, see logs above"
            )

        logger.info("Application has successfully shut down")
