from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import and_f, Command

from app.db import Database, UserRepository, WordRepository
from app.config import settings
from app.keyboards import adminMenu


router = Router()

router.message.filter(F.from_user.id == settings.ADMIN_ID)
router.callback_query.filter(F.from_user.id == settings.ADMIN_ID)

@router.message(Command(commands=['menu']))
async def start(message: Message):
    text = """
👋 Salom! Shodmon, Xush kelibsiz

Bugun nima qilamiz 🤔? ✨  

Boshlaymizmi? 😊
"""
    await message.answer(text, reply_markup=adminMenu())

@router.callback_query(F.data == "total_stats")
async def total_stats(callback: CallbackQuery):
    async with Database() as db:
        user_repo = UserRepository(db)
        word_repo = WordRepository(db)

        user_count = await user_repo.count_users()
        word_stats = await word_repo.get_stats()

    text = (
        "📊 <b>Bot statistikasi</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{user_count}</b>\n"
        f"📚 So'zlar: <b>{word_stats['total']}</b>\n"
        f"🔊 O'qilishi bilan: <b>{word_stats['with_phonetic']}</b>\n"
        f"🎧 Audio bilan: <b>{word_stats['with_audio']}</b>\n"
        f"🖼️ Rasm bilan: <b>{word_stats['with_image']}</b>"
    )
    await callback.answer()
    await callback.message.answer(text, parse_mode="HTML")


@router.callback_query(F.data == "daily_stats")
async def daily_stats(callback: CallbackQuery):
    async with Database() as db:
        user_repo = UserRepository(db)
        word_repo = WordRepository(db)

        user_count = await user_repo.count_daily_users()
        word_stats = await word_repo.get_daily_stats()

    text = (
        "📊 <b>Botning kunlik statistikasi</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{user_count}</b>\n"
        f"📚 So'zlar: <b>{word_stats['total']}</b>\n"
        f"🔊 O'qilishi bilan: <b>{word_stats['with_phonetic']}</b>\n"
        f"🎧 Audio bilan: <b>{word_stats['with_audio']}</b>\n"
        f"🖼️ Rasm bilan: <b>{word_stats['with_image']}</b>"
    )
    await callback.answer()
    await callback.message.answer(text, parse_mode="HTML")

@router.callback_query(F.data == "weekly_stats")
async def weekly_stats(callback: CallbackQuery):
    async with Database() as db:
        user_repo = UserRepository(db)
        word_repo = WordRepository(db)

        user_count = await user_repo.count_weekly_users()
        word_stats = await word_repo.get_weekly_stats()

    text = (
        "📊 <b>Bot haftalik statistikasi</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{user_count}</b>\n"
        f"📚 So'zlar: <b>{word_stats['total']}</b>\n"
        f"🔊 O'qilishi bilan: <b>{word_stats['with_phonetic']}</b>\n"
        f"🎧 Audio bilan: <b>{word_stats['with_audio']}</b>\n"
        f"🖼️ Rasm bilan: <b>{word_stats['with_image']}</b>"
    )
    await callback.answer()
    await callback.message.answer(text, parse_mode="HTML")


@router.callback_query(F.data == "monthly_stats")
async def montly_stats(callback: CallbackQuery):
    async with Database() as db:
        user_repo = UserRepository(db)
        word_repo = WordRepository(db)

        user_count = await user_repo.count_monthly_users()
        word_stats = await word_repo.get_monthly_stats()

    text = (
        "📊 <b>Bot oylik statistikasi</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{user_count}</b>\n"
        f"📚 So'zlar: <b>{word_stats['total']}</b>\n"
        f"🔊 O'qilishi bilan: <b>{word_stats['with_phonetic']}</b>\n"
        f"🎧 Audio bilan: <b>{word_stats['with_audio']}</b>\n"
        f"🖼️ Rasm bilan: <b>{word_stats['with_image']}</b>"
    )
    await callback.answer()
    await callback.message.answer(text, parse_mode="HTML")