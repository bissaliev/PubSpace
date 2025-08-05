import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.authentication_backend import JWTAuthenticationBackend
from src.auth.exceptions import UserNotExists
from src.db.database import get_db
from src.managers.user_manager import UserManager
from src.models.users import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
TokenDeps = Annotated[OAuth2PasswordBearer, Depends(oauth2_scheme)]
SessionDeps = Annotated[AsyncSession, Depends(get_db)]


async def get_user_manager(session: SessionDeps):
    yield UserManager(session)


UserManagerDeps = Annotated[UserManager, Depends(get_user_manager)]


def get_auth_backend(user_manager: UserManagerDeps):
    return JWTAuthenticationBackend(user_manager)


JWTAuthBackendDeps = Annotated[
    JWTAuthenticationBackend, Depends(get_auth_backend)
]


async def get_current_user(
    token: TokenDeps, auth_backend: JWTAuthBackendDeps
) -> User:
    return await auth_backend.get_current_user(token)


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_superuser(user: CurrentUser) -> User:
    if not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    return user


async def get_active_user(user: Annotated[User, Depends(get_current_user)]):
    if not user.is_active:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user


async def get_verified_user(user: Annotated[User, Depends(get_active_user)]):
    if not user.is_verified:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unverified user"
        )
    return user


async def get_user_or_404(
    id: uuid.UUID, user_manager: UserManagerDeps
) -> User:
    try:
        user = await user_manager.get(id)
        return user
    except UserNotExists as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e


UserDeps = Annotated[User, Depends(get_user_or_404)]
