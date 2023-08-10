import logging
from typing import cast

from pydantic import BaseSettings, PostgresDsn, validator


class NatsConfig(BaseSettings):
    nats_url: list[str] = ["nats://localhost:4222"]


class TelegramConfig(BaseSettings):
    token: str = "Ага попався!"


class LoggingConfig(BaseSettings):
    level: int = logging.DEBUG
    format: str = logging.BASIC_FORMAT


class DatabaseConfig(BaseSettings):
    server: str = "localhost"
    port: str = "54324"
    user: str = "postgres"
    password: str = "postgres"
    db: str = ""
    dsn: PostgresDsn | None = None

    @validator("dsn", always=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, str]) -> str:
        if isinstance(v, str):
            return v
        return cast(
            str,
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                user=values.get("user"),
                password=values.get("password"),
                host=values.get("server"),
                port=values.get("port"),
                path=f"/{values.get('db') or ''}",
            ),
        )


class Config(BaseSettings):
    nats: NatsConfig = NatsConfig()
    telegram: TelegramConfig = TelegramConfig()
    logging: LoggingConfig = LoggingConfig()
    database: DatabaseConfig = DatabaseConfig()

    class Config:
        env_file = ".env"
        env_nested_delimiter = "."
