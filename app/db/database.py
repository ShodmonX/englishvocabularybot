import logging
import asyncpg
import asyncio
import ssl

from app.config import settings

class Database:
    def __init__(self):
        self.dsn = settings.DSN
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.dsn, min_size=2, max_size=10, statement_cache_size=0)
        logging.info("Database connected")

    async def disconnect(self):
        if self.pool:
            try:
                await asyncio.wait_for(self.pool.close(), timeout=5)
            except asyncio.TimeoutError:
                logging.warning("⚠️ pool.close() juda uzoq davom etdi — majburan to‘xtatildi")

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
        
    async def fetchval(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)
        
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.disconnect()
        

async def init_db_schema():
    """
    Jadvallarni yangidan yaratadi.
    Agar mavjud bo'lsa, avval o'chiradi.
    """
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    pool = await asyncpg.create_pool(
        dsn=settings.DSN,
        min_size=2,
        max_size=10,
        ssl=ssl_context
    )

    logging.info("✅ Database connected")

    async with pool.acquire() as conn:
        try:
            logging.info("⚙️ Jadval tuzilmasi yangilanmoqda...")

            await conn.execute("""
            DROP TABLE IF EXISTS user_words CASCADE;
            DROP TABLE IF EXISTS words CASCADE;
            DROP TABLE IF EXISTS users CASCADE;
            """)

            await conn.execute("""
            CREATE TABLE users (
                id BIGSERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """)

            await conn.execute("""
            CREATE TABLE words (
                id BIGSERIAL PRIMARY KEY,
                word TEXT UNIQUE NOT NULL,
                phonetic TEXT,
                meanings JSONB,
                audio_url TEXT,
                telegram_audio_id TEXT,
                telegram_image_id TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            """)

            await conn.execute("""
            CREATE TABLE user_words (
                id BIGSERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
                word_id BIGINT REFERENCES words(id) ON DELETE CASCADE,
                level SMALLINT DEFAULT 0,
                progress REAL DEFAULT 0.0,
                last_reviewed TIMESTAMP DEFAULT NOW(),
                UNIQUE (user_id, word_id)
            );
            """)

            logging.info("✅ Barcha jadvallar muvaffaqiyatli yaratildi.")

        except Exception as e:
            logging.exception(f"❌ Xatolik: {e}")

    # Poolni yopishda timeout bilan kutish
    try:
        await asyncio.wait_for(pool.close(), timeout=5)
    except asyncio.TimeoutError:
        logging.warning("⚠️ pool.close() juda uzoq davom etdi — majburan to‘xtatildi")

    logging.info("✅ Database disconnected")


