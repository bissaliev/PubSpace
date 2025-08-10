from typing import Any

from sqlalchemy import delete, exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, id: int) -> User | None:
        stmt = select(User).where(User.id == id)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def list(self) -> list[User]:
        stmt = select(User)
        return (await self.session.execute(stmt)).scalars().all()

    async def create(self, **create_data: Any) -> User:
        user = User(**create_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, id: int, **update_user: Any) -> User:
        stmt = update(User).where(User.id == id).values(**update_user).returning(User)
        result = (await self.session.execute(stmt)).scalar()
        await self.session.commit()
        return result

    async def delete(self, id: int) -> None:
        stmt = delete(User).where(User.id == id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def exists(self, **filters: Any) -> bool:
        stmt = select(
            exists().where(*(getattr(User, k) == v for k, v in filters.items()))
        )
        result = await self.session.execute(stmt)
        return result.scalar()
