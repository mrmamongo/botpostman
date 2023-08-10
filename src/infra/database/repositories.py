from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.database.models import Subscriber as SubscriberModel
from src.application.subscribers.dto import Subscriber
from src.application.subscribers.interfaces import SubscriberRepo


class DatabaseSubscriberRepo(SubscriberRepo):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> Sequence[Subscriber]:
        return [
            Subscriber.from_orm(sub) for sub in (await self.session.scalars(select(SubscriberModel))).fetchall()
        ]

    async def get_by_username(self, subscriber_username: str) -> Subscriber | None:
        return (
            await self.session.execute(
                select(SubscriberModel)
                .where(subscriber_username == SubscriberModel.telegram_username)
                .limit(1)
            )
        ).one_or_none()

    async def create(self, subscriber: Subscriber) -> None:
        model = SubscriberModel()
        model.telegram_id = subscriber.telegram_id
        model.telegram_username = subscriber.telegram_username

        self.session.add(model)
        await self.session.commit()
