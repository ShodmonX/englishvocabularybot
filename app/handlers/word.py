from aiogram import Router, F
from aiogram.types import Message, FSInputFile, CallbackQuery, URLInputFile

import logging
import os

from .utils import dataPreprocessing, deleteFlashcard, generateFlashcard
from app.services import DictionaryAPI
from app.db import Database, WordRepository
from app.keyboards import audioButton


router = Router()

@router.message()
async def getDefinitions(message: Message):
    founded, text, image, word, hasAudio, imagePath, inDB = await  dataPreprocessing(word=message.text)
    if not founded:
        await message.reply(text="Word not found")
        return
    else:
        sent = await message.reply_photo(photo=image, caption=text, reply_markup=audioButton(word) if hasAudio else None)
        if not inDB:
            async with Database() as db:
                wordRepo = WordRepository(db)
                await wordRepo.update_image(word, sent.photo[-1].file_id)
        if imagePath and os.path.exists(imagePath):
            deleteFlashcard(imagePath)
    


@router.callback_query(F.data.startswith("sendAudio:"))
async def senAudio(callback: CallbackQuery):
    word = callback.data.split(":", 1)[1]

    async with Database() as db:
        wordRepo = WordRepository(db)
        data = await wordRepo.get_word(word)
        url = data.get("audio_url", "")
        try:
            sent = await callback.message.reply_audio(URLInputFile(url, filename=f"{word}.mp3"))
            await callback.answer()
        except Exception as e:
            await callback.answer("Audio not found")
            logging.error(e)

        if not data.get("telegram_audio_id", ""):
            await wordRepo.update_audio(word, sent.audio.file_id)