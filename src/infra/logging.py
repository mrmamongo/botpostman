import logging

from src.config import LoggingConfig


def setup_logging(config: LoggingConfig):
    logging.basicConfig(level=config.level, format=config.format)
