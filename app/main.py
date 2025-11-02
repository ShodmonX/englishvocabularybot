from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

import logging

from .config import settings
from .handlers import routers


async def run():
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.include_routers(*routers)

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(e)
    finally:
        await bot.session.close()


