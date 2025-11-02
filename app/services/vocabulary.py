import aiohttp
import logging


class DictionaryAPI:
    def __init__(self):
        self.url = 'https://api.dictionaryapi.dev/api/v2/entries/en/'

    async def getData(self, word: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + word) as response:
                if response.status == 200:
                    logging.info(f"Word {word} found in dictionary")
                    return await response.json()
                logging.info(f"Word {word} not found in dictionary")
                return []