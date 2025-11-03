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
    
    async def count_users(self):
        query = "SELECT COUNT(*) FROM users;"
        return await self.db.fetchval(query)
    
    async def count_daily_users(self):
        query = """
            SELECT COUNT(*) FROM users
            WHERE (created_at AT TIME ZONE 'Asia/Tashkent')::date = (CURRENT_DATE AT TIME ZONE 'Asia/Tashkent');
        """
        return await self.db.fetchval(query)
    
    async def count_weekly_users(self):
        query = """
            SELECT COUNT(*) FROM users
            WHERE (created_at AT TIME ZONE 'Asia/Tashkent')::date >= (CURRENT_DATE AT TIME ZONE 'Asia/Tashkent') - INTERVAL '7 days';
        """
        return await self.db.fetchval(query)
    
    async def count_monthly_users(self):
        query = """
            SELECT COUNT(*) FROM users
            WHERE (created_at AT TIME ZONE 'Asia/Tashkent')::date >= (CURRENT_DATE AT TIME ZONE 'Asia/Tashkent') - INTERVAL '30 days';
        """
        return await self.db.fetchval(query)
