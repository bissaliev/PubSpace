from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import (
    CurrentUser,
    UserDeps,
    UserManagerDeps,
    get_superuser,
)
from src.auth.exceptions import InvalidPassword, UserAlreadyExists
from src.schemas.users import UserCreate, UserRead, UserUpdate

router = APIRouter()


@router.get(
    "/",
    response_model=list[UserRead],
    dependencies=[Depends(get_superuser)],
    summary="Список пользователей",
)
async def get_users(
    user_manager: UserManagerDeps, limit: int = 10, offset: int = 0
):
    return await user_manager.list(limit, offset)


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
)
async def register(user_create: UserCreate, user_manager: UserManagerDeps):
    try:
        created_user = await user_manager.create(user_create)
    except UserAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="REGISTER_USER_ALREADY_EXISTS",
        ) from e
    except InvalidPassword as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="REGISTER_INVALID_PASSWORD",
        ) from e
    return created_user


@router.get("/me", response_model=UserRead, summary="Профиль пользователя")
async def me(user: CurrentUser):
    return user


@router.patch("/me", response_model=UserRead, summary="Обновление профиля")
async def update_me(
    user: CurrentUser, user_update: UserUpdate, user_manager: UserManagerDeps
):
    return await user_manager.update(user, user_update, safe=True)


@router.get(
    "/{id}",
    response_model=UserRead,
    dependencies=[Depends(get_superuser)],
    summary="Получение пользователя по id",
)
async def get_user(user: UserDeps):
    return user


@router.patch(
    "/{id}",
    response_model=UserRead,
    dependencies=[Depends(get_superuser)],
    summary="Обновление данных пользователя",
)
async def update_user(
    user: UserDeps, user_update: UserUpdate, user_manager: UserManagerDeps
):
    return await user_manager.update(user, user_update, safe=False)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_superuser)],
    summary="Удаление пользователя",
)
async def delete_user(user: UserDeps, user_manager: UserManagerDeps):
    return await user_manager.delete(user)
