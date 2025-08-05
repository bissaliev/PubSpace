from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.api.dependencies import JWTAuthBackendDeps
from src.schemas.users import Token

router = APIRouter()


@router.post(
    "/login", response_model=Token, summary="Получение токена аутентификации"
)
async def login(
    auth_backend: JWTAuthBackendDeps,
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    return await auth_backend.login(credentials.username, credentials.password)
