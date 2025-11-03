from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def adminMenu():
    builder = InlineKeyboardBuilder(
        markup=[
            [InlineKeyboardButton(text="📊 Statistika", callback_data="total_stats"), InlineKeyboardButton(text="1️⃣ Kunlik statistika", callback_data="daily_stats")],
            [InlineKeyboardButton(text="7️⃣ Haftalik statistika", callback_data="weekly_stats"), InlineKeyboardButton(text="3️⃣0️⃣ Oylik statistika", callback_data="monthly_stats")],
        ]
    )

    return builder.as_markup()