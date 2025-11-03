from aiogram import BaseMiddleware
from aiogram.types import Message

import logging
from typing import Callable, Awaitable, Dict, Any

from app.db import UserRepository, Database
from app.config import settings

class StartMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        logging.info(f"Start middleware called for user {event.from_user.id} - {event.from_user.full_name}")
        db = Database()
        await db.connect()
        userRepo = UserRepository(db)
        user = await userRepo.get_user(event.from_user.id)
        if not user:
            text = (
                f"Botda yangi foydalanuvchi: {event.from_user.full_name}\n"
                f"Telegram ID: {event.from_user.id}\n"
                f"Username: @{event.from_user.username}"
            )
            await event.bot.send_message(chat_id=settings.ADMIN_ID, text=text)
            await userRepo.add_user(event.from_user.id, event.from_user.full_name, event.from_user.username)
        await db.disconnect()
        return await handler(event, data)
    