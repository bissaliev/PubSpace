import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from src.auth.exceptions import UserAlreadyExists, UserNotExists
from src.auth.hashing_password import PasswordHelper
from src.models.users import User
from src.schemas.users import UserCreate, UserUpdate


class UserManager:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.password_helper = PasswordHelper()

    async def list(self, limit: int = 10, offset: int = 0) -> list[User]:
        users = (
            await self.session.scalars(
                select(User).limit(limit).offset(offset)
            )
        ).all()
        return users

    async def create(self, user_create: UserCreate) -> User:
        existing_user = (
            await self.session.scalars(
                select(User).where(User.email == user_create.email)
            )
        ).first()
        if existing_user is not None:
            raise UserAlreadyExists()
        user_dict = user_create.model_dump()
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        created_user = User(**user_dict)
        self.session.add(created_user)
        await self.session.commit()
        await self.session.refresh(created_user)
        return created_user

    async def get(self, id: uuid.UUID) -> User:
        user = (
            await self.session.scalars(select(User).where(User.id == id))
        ).first()
        if not user:
            raise UserNotExists()
        return user

    async def get_by_email(self, email: str) -> User:
        user = (
            await self.session.scalars(select(User).where(User.email == email))
        ).first()
        if not user:
            raise UserNotExists()
        return user

    async def update(
        self, user: User, user_update: UserUpdate, safe: bool = False
    ) -> User:
        exclude_field = {}
        if safe:
            exclude_field |= {"is_superuser", "is_active", "is_verified"}
        user_dict = user_update.model_dump(
            exclude_unset=True, exclude=exclude_field
        )
        return await self._update(user, user_dict)

    async def _update(self, user: User, update_dict: dict[str, Any]):
        for field, value in update_dict.items():
            if field == "email":
                try:
                    await self.get_by_email(value)
                    raise UserAlreadyExists()
                except UserNotExists:
                    setattr(user, field, value)
                    user.is_verified = False
            elif field == "password":
                await self.validate_password(value)
                setattr(user, field, self.password_helper.hash(value))
            else:
                setattr(user, field, value)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.commit()

    async def _get_user(self, statement: Select) -> User | None:
        results = await self.session.execute(statement)
        return results.unique().scalar_one_or_none()

    async def validate_password(self, password: str): ...

    async def authenticate(self, email: str, password: str) -> User | None:
        try:
            user = await self.get_by_email(email)
        except UserNotExists:
            return None
        if not self.password_helper.verify(password, user.hashed_password):
            return None
        return user
