from .database import Database


class UserRepository:
    def __init__(self, db: Database):
        self.db = db

    async def add_user(self, telegram_id, full_name, username):
        query = """
            INSERT INTO users (telegram_id, full_name, username)
            VALUES ($1, $2, $3)
            ON CONFLICT (telegram_id) DO NOTHING;
        """

        await self.db.execute(query, telegram_id, full_name, username)

    async def get_user(self, telegram_id):
        query = """
            SELECT * FROM users
            WHERE telegram_id = $1;
        """
        return await self.db.fetchrow(query, telegram_id)
