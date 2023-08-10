from contextlib import asynccontextmanager
from typing import Callable, cast, AsyncGenerator, AsyncContextManager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import DatabaseConfig


def setup_database(
    config: DatabaseConfig,
) -> tuple[Callable[[], AsyncContextManager[AsyncSession]], AsyncEngine]:
    engine = create_async_engine(
        cast(str, config.dsn),
        pool_pre_ping=True,
    )

    session_local = async_sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async def session() -> AsyncGenerator[AsyncSession, None]:
        async with session_local() as session_:
            yield session_

    return asynccontextmanager(session), engine
