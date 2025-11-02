from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def audioButton(word: str):
    builder = InlineKeyboardBuilder()
    button = InlineKeyboardButton(
        text = "Audio",
        callback_data=f"sendAudio:{word}"
    )
    builder.add(button)

    return builder.as_markup()