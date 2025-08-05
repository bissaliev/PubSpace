from datetime import timedelta

from fastapi import HTTPException, status

from src.auth.exceptions import UserNotExists
from src.auth.jwt import create_access_token, read_token
from src.core.config import settings
from src.managers.user_manager import UserManager
from src.models.users import User
from src.schemas.users import Token


class JWTAuthenticationBackend:
    def __init__(self, user_manager: UserManager):
        self.user_manager = user_manager

    async def login(self, email: str, password: str) -> Token:
        user = await self.user_manager.authenticate(email, password)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        expires_delta = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECOND)
        access_token = create_access_token(
            {"sub": user.email}, expires_delta=expires_delta
        )
        return Token(access_token=access_token, token_type="bearer")

    async def get_current_user(self, token: str) -> User:
        try:
            payload = read_token(token)
            email = payload.get("sub")
            user = await self.user_manager.get_by_email(email)
        except UserNotExists as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e
        return user
