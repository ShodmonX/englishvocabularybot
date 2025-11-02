import json
import logging

from .database import Database


class WordRepository:
    def __init__(self, db: Database):
        self.db = db

    async def add_word(self, word: str, meanings: list[dict], phonetic: str | None = None, audio_url: str | None = None):
        query = """
            INSERT INTO words (word, phonetic, meanings, audio_url)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (word) DO NOTHING;
        """

        await self.db.execute(query, word, phonetic, json.dumps(meanings), audio_url)

    async def get_word(self, word: str):
        query = """
            SELECT * FROM words
            WHERE word = $1;
        """
        row = await self.db.fetchrow(query, word)
        if not row:
            return None

        data = dict(row)
        if data.get("meanings"):
            if isinstance(data["meanings"], str):
                try:
                    data["meanings"] = json.loads(data["meanings"])
                except Exception as e:
                    logging.warning(f"Invalid meanings JSON for word {data.get('word')}: {e}")
                    data["meanings"] = []
        else:
            data["meanings"] = []

        return data
    
    async def update_audio(self, word: str, telegram_audio_id: str):
        query = """
            UPDATE words
            SET telegram_audio_id = $2
            WHERE word = $1;
        """
        await self.db.execute(query, word, telegram_audio_id)

    async def update_image(self, word: str, telegram_image_id: str):
        query = """
            UPDATE words
            SET telegram_image_id = $2
            WHERE word = $1;
        """
        await self.db.execute(query, word, telegram_image_id)
