from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.hashing_password import PasswordHelper
from src.dtos.users import UserCreateDTO, UserReadDTO, UserUpdateDTO
from src.exceptions.users import UserAlreadyExists, UserNotExists
from src.models.users import User
from src.repositories.user_repo import UserRepository


class UserService:
    def __init__(self, session: AsyncSession, repo: UserRepository) -> None:
        self.session = session
        self.repo = repo
        self.password_helper = PasswordHelper()

    async def create_user(self, create_user: UserCreateDTO) -> UserReadDTO:
        exists_user = await self.repo.exists(email=create_user.email)
        if exists_user:
            raise UserAlreadyExists()
        new_user = await self.repo.create(
            email=create_user.email,
            hashed_password=self.password_helper.hash(create_user.password),
        )
        return self.to_dto(new_user)

    async def get_users(self) -> list[UserReadDTO]:
        users = await self.repo.list()
        return [self.to_dto(u) for u in users]

    async def get_user(self, id: int) -> UserReadDTO:
        user = await self.repo.get_by_id(id)
        if not user:
            raise UserNotExists()
        return self.to_dto(user)

    async def update_user(self, id: int, update_user: UserUpdateDTO) -> UserReadDTO:
        exists = await self.repo.exists(id=id)
        if not exists:
            raise UserNotExists()
        updated_user = await self.repo.update(id, **self.from_dto(update_user))
        return self.to_dto(updated_user)

    async def delete_user(self, id: int) -> None:
        exists = await self.repo.exists(id=id)
        if not exists:
            raise UserNotExists()
        await self.repo.delete(id)

    @staticmethod
    def to_dto(user: User) -> UserReadDTO:
        return UserReadDTO(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            birth_date=user.birth_date,
            is_active=user.is_active,
            is_verified=user.is_verified,
            is_superuser=user.is_superuser,
            created_at=user.create_at,
        )

    @staticmethod
    def from_dto(user_dto: UserUpdateDTO) -> dict[str, Any]:
        return {k: v for k, v in user_dto.__dict__.items() if v is not None}
