import asyncio
import logging

from app.main import run
from app.db import init_db_schema

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-8s %(name)-15s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

async def main():
    # await init_db_schema()
    await run()

if __name__ == "__main__":
    asyncio.run(main())