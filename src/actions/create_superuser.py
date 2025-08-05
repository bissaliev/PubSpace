import asyncio
from contextlib import asynccontextmanager

from src.api.dependencies import get_user_manager
from src.db.database import get_db
from src.schemas import SuperUserCreate

user_manager_context = asynccontextmanager(get_user_manager)
get_db_context = asynccontextmanager(get_db)


async def create_superuser():
    async with get_db_context() as db:
        async with user_manager_context(db) as manager:
            superuser = SuperUserCreate(
                email="admin@admin.com",
                password="admin",
                is_superuser=True,
                is_active=True,
                is_verified=True,
            )
            await manager.create(superuser)


if __name__ == "__main__":
    asyncio.run(create_superuser())
