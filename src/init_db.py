import asyncio

from src.db.database import async_engine
from src.models.base import Base


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main():
    await init_db()


if __name__ == "__main__":
    asyncio.run(main())
