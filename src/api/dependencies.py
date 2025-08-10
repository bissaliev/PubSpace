import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.exceptions.users import InvalidVerifyToken, UserNotExists
from src.models.users import User
from src.repositories.user_repo import UserRepository
from src.services.auth_service import AuthService
from src.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
TokenDeps = Annotated[OAuth2PasswordBearer, Depends(oauth2_scheme)]


SessionDeps = Annotated[AsyncSession, Depends(get_db)]


async def get_user_service(session: SessionDeps) -> AsyncGenerator[UserService, None]:
    yield UserService(session, UserRepository(session))


async def get_auth_service(session: SessionDeps) -> AsyncGenerator[AuthService, None]:
    yield AuthService(session, UserRepository(session))


UserServiceDeps = Annotated[UserService, Depends(get_user_service)]
AuthServiceDeps = Annotated[AuthService, Depends(get_auth_service)]


async def get_current_user(token: TokenDeps, service: AuthServiceDeps) -> User:
    try:
        return await service.get_current_user(token)
    except (UserNotExists, InvalidVerifyToken):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_superuser(user: CurrentUser) -> User:
    if not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return user


async def get_active_user(user: Annotated[User, Depends(get_current_user)]) -> User:
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user


async def get_verified_user(user: Annotated[User, Depends(get_active_user)]) -> User:
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unverified user"
        )
    return user


async def get_user_or_404(id: uuid.UUID, user_service: UserServiceDeps) -> User:
    try:
        user = await user_service.repo.get_by_id(id)
        return user
    except UserNotExists as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e


UserDeps = Annotated[User, Depends(get_user_or_404)]
