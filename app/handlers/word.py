from aiogram import Router, F
from aiogram.types import Message, FSInputFile, CallbackQuery, URLInputFile
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums.chat_action import ChatAction
from aiogram.utils.chat_action import ChatActionSender

import logging
import os

from .utils import dataPreprocessing, deleteFile, preprocessAudio, generateFlashcard
from app.services import DictionaryAPI
from app.db import Database, WordRepository
from app.keyboards import audioButton


router = Router()

@router.message()
async def getDefinitions(message: Message):
    founded, text, image, word, pronunciation, hasAudio, imagePath, inDB = await  dataPreprocessing(word=message.text.lower())
    if not founded:
        text = """
😕 Kechirasiz, bu so‘z bo‘yicha ma’lumot topilmadi.

Iltimos, so‘zni to‘g‘ri yozilganini tekshirib ko‘ring yoki boshqa so‘zni kiriting 🔎 
"""
        await message.reply(text)
        return
    else:
        try:
            sent = await message.reply_photo(photo=image, caption=text, reply_markup=audioButton(word) if hasAudio else None)
            if not inDB:
                async with Database() as db:
                    wordRepo = WordRepository(db)
                    await wordRepo.update_image(word, sent.photo[-1].file_id)
            if imagePath and os.path.exists(imagePath):
                deleteFile(imagePath)
        except TelegramBadRequest as e:
            if "file is not found" in str(e).lower():
                image = generateFlashcard(word, pronunciation)
                sent = await message.reply_photo(photo=FSInputFile(image), caption=text, reply_markup=audioButton(word) if hasAudio else None)
                async with Database() as db:
                    wordRepo = WordRepository(db)
                    await wordRepo.update_image(word, sent.photo[-1].file_id)
                if imagePath and os.path.exists(imagePath):
                    deleteFile(imagePath)
        except Exception as e:
            logging.error(f"Error sending photo: {e}")


@router.callback_query(F.data.startswith("sendAudio:"))
async def sendAudio(callback: CallbackQuery):
    word = callback.data.split(":", 1)[1]

    async with Database() as db:
        wordRepo = WordRepository(db)
        data = await wordRepo.get_word(word.lower())
        url = data.get("audio_url", "")
        audio_id = data.get("telegram_audio_id", "")
        try:
            if not audio_id:
                async with ChatActionSender(bot = callback.bot, chat_id = callback.message.chat.id, action = ChatAction.UPLOAD_VOICE):
                    voice = await preprocessAudio(url)
                    sent = await callback.message.reply_voice(voice=FSInputFile(voice))
                    await wordRepo.update_audio(word, sent.voice.file_id)
                    if voice:
                        deleteFile(voice)
            else:
                try:
                    sent = await callback.message.reply_voice(audio_id)
                except TelegramBadRequest as e:
                    if "file is not found" in str(e).lower():
                        async with ChatActionSender(bot = callback.bot, chat_id = callback.message.chat.id, action = ChatAction.UPLOAD_VOICE):
                            voice = await preprocessAudio(url)
                            sent = await callback.message.reply_voice(voice=FSInputFile(voice))
                            await wordRepo.update_audio(word, sent.voice.file_id)
                            if voice:
                                deleteFile(voice)
        except Exception as e:
                await callback.answer("Audio not found")
                logging.error(e)

        await callback.answer()
