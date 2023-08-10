from abc import ABC, abstractmethod
from typing import Sequence

from src.application.subscribers.dto import Subscriber


class SubscriberRepo(ABC):
    @abstractmethod
    async def get_all(self) -> Sequence[Subscriber]:
        pass

    @abstractmethod
    async def get_by_username(self, subscriber_username: str) -> Subscriber:
        pass

    @abstractmethod
    async def create(self, subscriber: Subscriber) -> None:
        pass

    # ... more methods
