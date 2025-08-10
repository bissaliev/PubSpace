from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.hashing_password import PasswordHelper
from src.auth.jwt import create_access_token, read_token
from src.core.config import settings
from src.exceptions.users import InvalidVerifyToken, UserNotExists
from src.models.users import User
from src.repositories.user_repo import UserRepository
from src.schemas.users import Token


class AuthService:
    def __init__(self, session: AsyncSession, repo: UserRepository) -> None:
        self.session = session
        self.repo = repo
        self.password_helper = PasswordHelper()

    async def login(self, email: str, password: str) -> Token:
        user = await self.authenticate(email, password)
        if not user:
            raise UserNotExists("User not exists")
        expires_delta = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECOND)
        access_token = create_access_token(
            {"sub": user.email}, expires_delta=expires_delta
        )
        return Token(access_token=access_token, token_type="bearer")

    async def authenticate(self, email: str, password: str) -> User | None:
        user = await self.repo.get_by_email(email)
        if not user:
            return None
        if not self.password_helper.verify(password, user.hashed_password):
            return None
        return user

    async def get_current_user(self, token: str) -> User:
        payload = read_token(token)
        if not payload:
            raise InvalidVerifyToken("Invalid token")
        email = payload.get("sub")
        if not email:
            raise InvalidVerifyToken("Invalid token")
        user = await self.repo.get_by_email(email)
        if not user:
            raise UserNotExists("User not exists")
        return user
