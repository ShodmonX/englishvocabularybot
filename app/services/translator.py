import aiohttp
import logging

from app.config import settings

class Translator:
    def __init__(self):
        self.url = "https://translation.googleapis.com/language/translate/v2"
        self.target = "uz"
        self.api_key = settings.GOOGLE_TRANSLATE_API_KEY

    async def translate(self, text: str) -> str:
        params = {
            "key": self.api_key,
            "q": text,
            "target": self.target,
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, params=params) as response:
                if response.status == 200:
                    logging.info("Translation successful")
                    data = await response.json()
                    return data["data"]["translations"][0]["translatedText"]
                logging.info("Translation failed")
                return ""