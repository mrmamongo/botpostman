import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.application.postman.dto import DispatchMessage
from src.application.postman.service import PostmanService
from src.application.subscribers.dto import Subscriber
from src.application.subscribers.interfaces import SubscriberRepo

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("subscribe"))
async def command_subscribe(message: Message, sub_repo: SubscriberRepo) -> None:
    sub: Subscriber | None = await sub_repo.get_by_username(message.from_user.username)

    if sub is not None:
        await message.reply("Already subscribed!")
        return

    sub = Subscriber(
        telegram_id=str(message.from_user.id), telegram_username=message.from_user.username
    )
    await sub_repo.create(sub)
    await message.reply("Subscribed!")


@router.message(Command("send"))
async def command_start_dispatch(message: Message, postman: PostmanService) -> None:
    msg = DispatchMessage(
        from_username=message.from_user.username, message=message.text
    )
    logger.info(f"Performing dispatch: {msg!r}")
    await postman.perform_dispatch(msg)
