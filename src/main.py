import asyncio
import logging
import os

from src.app import Application
from src.config import Config

logger = logging.getLogger(__name__)


async def run() -> None:
    config = Config()  # type: ignore
    application = await Application.from_config(config)

    try:
        await application.start()
    finally:
        await application.dispose()


def main() -> None:
    try:
        asyncio.run(run())
        exit(os.EX_OK)
    except SystemExit:
        exit(os.EX_OK)
    except Exception:
        logger.exception("Unexpected error occurred")
        exit(os.EX_SOFTWARE)


if __name__ == "__main__":
    main()
