from PIL import Image, ImageDraw, ImageFont
from aiogram.types import FSInputFile
import os
import random
import logging
import aiohttp
import subprocess

from app.db import WordRepository, Database
from app.services import DictionaryAPI, Translator


import logging
import json
from aiogram.types import FSInputFile

async def dataPreprocessing(word: str):
    """
    Generate a flashcard for a given word.

    Returns:
        tuple: (success, text_result, image_or_id, word, pronunciation, hasAudio, imagePath)
    """
    word = word.strip()

    try:
        data, inDB = await collectData(word)
        if not data:
            return False, "", None, word, "", False, None, True
        
        meanings = data.get("meanings", [])
        hasAudio = True if data.get("audio_url", "") else False
        pronunciation = data.get("phonetic", "")
        result = [f"Word: <b>{word}</b>"]
        if not inDB:
            imagePath = generateFlashcard(word, pronunciation)
            image = FSInputFile(imagePath, filename=f"{word}.png")

        else:
            imagePath = None
            image = data.get("telegram_image_id")

        for meaning in meanings[:2]:
            part = meaning.get("partOfSpeech", "")
            definitions = meaning.get("definitions", [])[:2]

            if definitions:
                result.append(f"\n<i>{part}</i>:")
                for i, d in enumerate(definitions, 1):
                    definition = d.get("definition", "")
                    example = d.get("example", "")
                    text = f"{i}. {definition}"
                    if example:
                        text += f"\n   <u>Example:</u> {example}"
                    result.append(text)

        return True, "\n".join(result), image, word, pronunciation, hasAudio, imagePath, inDB

    except Exception as e:
        logging.error(f"dataPreprocessing error: {e}")
        return False, "", None, word, "", False, None, True

async def collectData(word: str):
    data = {}
    inDB = False
    async with Database() as db:
        wordRepo = WordRepository(db)
        db_data = await wordRepo.get_word(word)
        if not db_data:
            api = DictionaryAPI()
            api_data = await api.getData(word)
            data["word"] = api_data[0].get("word", "")
            data["phonetic"]  = api_data[0].get("phonetic", "")
            data["meanings"] = await preprocessMeanings(api_data[0].get("meanings", []))
            url = None
            for i in api_data[0].get("phonetics", []):
                url = i.get("audio", "")
                if url: break
            data["audio_url"] = url

            await wordRepo.add_word(data["word"], data["meanings"], data["phonetic"], data["audio_url"])

        else:
            inDB = True
            data["word"] = db_data.get("word", "")
            data["phonetic"] = db_data.get("phonetic", "")
            data["meanings"] = db_data.get("meanings", [])
            data["telegram_audio_id"] = db_data.get("telegram_audio_id", "")
            data["audio_url"] = db_data.get("audio_url", "")
            data["telegram_image_id"] = db_data.get("telegram_image_id", "")

    return data, inDB

async def preprocessMeanings(meanings: list[dict]) -> list[dict]:
    translator = Translator()

    for meaning in meanings:
        definitions = meaning.get("definitions", [])
        if not definitions:
            continue

        for d in definitions:
            definition = d.get("definition", "")
            if not definition:
                continue

            try:
                translated = await translator.translate(definition)
                d["definition_original"] = definition
                d["definition"] = translated
            except Exception as e:
                d["definition_original"] = definition
                d["definition"] = definition

    return meanings

def generateFlashcard(
    word: str,
    pronunciation: str,
    width=900,
    height=500,
    word_font_size=100,
    pron_font_size=55,
    output_path="flashcard.png"
):
    """Generate a stylish, readable vocabulary flashcard."""

    pastel_colors = [
        (240, 248, 255),  # Alice Blue
        (255, 250, 240),  # Floral White
        (245, 255, 250),  # Mint Cream
        (255, 240, 245),  # Lavender Blush
        (255, 255, 224),  # Light Yellow
        (240, 255, 240),  # Honeydew
    ]
    bg_color = random.choice(pastel_colors)

    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
    ]

    def get_font(size):
        for path in font_paths:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
        return ImageFont.load_default()

    word_font = get_font(word_font_size)
    pron_font = get_font(pron_font_size)

    def text_size(text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    word_w, word_h = text_size(word, word_font)
    pron_w, pron_h = text_size(pronunciation, pron_font)

    spacing = 25
    total_height = word_h + pron_h + spacing
    start_y = (height - total_height) // 2

    text_color = (30, 30, 30)

    shadow_offset = 2
    shadow_color = (180, 180, 180)

    draw.text(((width - word_w) // 2 + shadow_offset, start_y + shadow_offset), word, fill=shadow_color, font=word_font)
    draw.text(((width - word_w) // 2, start_y), word, fill=text_color, font=word_font)

    if pronunciation:
        draw.text(((width - pron_w) // 2 + shadow_offset, start_y + word_h + spacing + shadow_offset), pronunciation, fill=shadow_color, font=pron_font)
        draw.text(((width - pron_w) // 2, start_y + word_h + spacing), pronunciation, fill=text_color, font=pron_font)
    img.save(output_path)
    return output_path

def deleteFile(path: str):
    if os.path.exists(path):
        os.remove(path)
    
async def preprocessAudio(audio_url: str, output_path: str = "audio.ogg"):
    temp_file = "temp.mp3"

    async with aiohttp.ClientSession() as session:
        async with session.get(audio_url) as response:
            if response.status != 200:
                raise Exception(f"Audio yuklab olinmadi! Status: {response.status}")
            content = await response.read()
            with open(temp_file, "wb") as f:
                f.write(content)

    subprocess.run([
        "ffmpeg",
        "-i", temp_file,
        "-acodec", "libopus",
        "-b:a", "64k",
        output_path,
        "-y"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    os.remove(temp_file)

    return output_path
