import asyncio
from contextlib import asynccontextmanager

from src.auth.hashing_password import PasswordHelper
from src.db.database import get_db
from src.repositories.user_repo import UserRepository

get_db_context = asynccontextmanager(get_db)


async def create_superuser() -> None:
    async with get_db_context() as db:
        repo = UserRepository(db)
        pwd_helper = PasswordHelper()
        await repo.create(
            email="admin@admin.com",
            hashed_password=pwd_helper.hash("admin"),
            is_superuser=True,
            is_active=True,
            is_verified=True,
        )


if __name__ == "__main__":
    asyncio.run(create_superuser())
