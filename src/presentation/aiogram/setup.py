from aiogram import Dispatcher

from src.presentation.aiogram.router import router


def setup_aiogram(dp: Dispatcher) -> None:
    dp.include_router(router)
