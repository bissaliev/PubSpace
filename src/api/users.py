from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import (
    CurrentUser,
    UserServiceDeps,
    get_superuser,
)
from src.dtos.users import UserUpdateDTO
from src.exceptions.users import UserAlreadyExists, UserNotExists
from src.schemas.users import UserCreate, UserRead, UserUpdate

router = APIRouter()


@router.get(
    "/",
    response_model=list[UserRead],
    dependencies=[Depends(get_superuser)],
    summary="Список пользователей",
)
async def get_users(user_service: UserServiceDeps) -> list[UserRead]:
    users = await user_service.get_users()
    return users


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
)
async def register(user_create: UserCreate, user_service: UserServiceDeps) -> UserRead:
    try:
        created_user = await user_service.create_user(user_create)
    except UserAlreadyExists as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="REGISTER_USER_ALREADY_EXISTS",
        ) from e
    return created_user


@router.get("/me", response_model=UserRead, summary="Профиль пользователя")
async def me(user: CurrentUser) -> UserRead:
    return user


@router.patch("/me", response_model=UserRead, summary="Обновление профиля")
async def update_me(
    user: CurrentUser, user_update: UserUpdate, user_service: UserServiceDeps
) -> UserRead:
    dto = UserUpdateDTO(**user_update.model_dump(exclude_unset=True))
    return await user_service.update_user(user.id, dto)


@router.get(
    "/{id}",
    response_model=UserRead,
    dependencies=[Depends(get_superuser)],
    summary="Получение пользователя по id",
)
async def get_user(id: int, user_service: UserServiceDeps) -> UserRead:
    try:
        return await user_service.get_user(id)
    except UserNotExists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not exists"
        ) from None


@router.patch(
    "/{id}",
    response_model=UserRead,
    dependencies=[Depends(get_superuser)],
    summary="Обновление данных пользователя",
)
async def update_user(
    id: int, user_update: UserUpdate, user_service: UserServiceDeps
) -> UserRead:
    try:
        dto = UserUpdateDTO(**user_update.model_dump(exclude_unset=True))
        return await user_service.update_user(id, dto)
    except UserNotExists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not exists"
        ) from None


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_superuser)],
    summary="Удаление пользователя",
)
async def delete_user(id: int, service: UserServiceDeps) -> None:
    try:
        await service.delete_user(id)
    except UserNotExists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not exists"
        ) from None
