from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from app.middlewares import StartMiddleware

router = Router()

router.message.middleware(StartMiddleware())

@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Hello!")

