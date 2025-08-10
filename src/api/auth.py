from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.api.dependencies import AuthServiceDeps
from src.schemas.users import Token

router = APIRouter()


@router.post("/login", response_model=Token, summary="Получение токена аутентификации")
async def login(
    service: AuthServiceDeps,
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    return await service.login(credentials.username, credentials.password)
