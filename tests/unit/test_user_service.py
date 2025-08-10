from typing import Any
from unittest.mock import AsyncMock

import pytest
from tests.utils.fake_user import fake_user, password

from src.dtos.users import UserCreateDTO, UserReadDTO, UserUpdateDTO
from src.exceptions.users import UserAlreadyExists, UserNotExists
from src.services.user_service import UserService


@pytest.mark.unit
class TestUserService:
    async def test_get_user(self) -> None:
        """Проверяем получение одного пользователя по его id"""
        user = fake_user()
        mock_repo = AsyncMock()
        mock_session = AsyncMock()
        mock_repo.get_by_id.return_value = user
        service = UserService(mock_session, mock_repo)
        result = await service.get_user(user.id)
        assert result.id == user.id
        mock_repo.get_by_id.assert_called_once_with(user.id)
        assert isinstance(result, UserReadDTO)

    async def test_get_user_not_exists(self) -> None:
        """Проверяем ошибку при получении пользователя, которого нет в базе"""
        mock_repo = AsyncMock()
        mock_session = AsyncMock()
        mock_repo.get_by_id.return_value = None
        service = UserService(mock_session, mock_repo)
        with pytest.raises(UserNotExists):
            await service.get_user(1)
        mock_repo.get_by_id.assert_called_once_with(1)

    async def test_get_users(self) -> None:
        """Проверяем получение списка пользователей"""
        users = [fake_user()]
        mock_repo = AsyncMock()
        mock_session = AsyncMock()
        mock_repo.list.return_value = users
        service = UserService(mock_session, mock_repo)
        result = await service.get_users()
        assert len(result) == len(users)
        assert result[0].id == users[0].id
        mock_repo.list.assert_called_once()
        assert isinstance(result[0], UserReadDTO)

    async def test_get_users_return_empty_list(self) -> None:
        """Проверяем получение пустого списка пользователей"""
        mock_repo = AsyncMock()
        mock_session = AsyncMock()
        mock_repo.list.return_value = []
        service = UserService(mock_session, mock_repo)
        result = await service.get_users()
        assert len(result) == 0
        mock_repo.list.assert_called_once()

    async def test_create_user_success(self) -> None:
        """Проверяем создание нового пользователя"""
        mock_repo = AsyncMock()
        mock_session = AsyncMock()
        user = fake_user()
        user_create_dto = UserCreateDTO(
            email=user.email,
            password=password,
        )
        mock_repo.exists.return_value = False
        mock_repo.create.return_value = fake_user()
        service = UserService(mock_session, mock_repo)
        result = await service.create_user(user_create_dto)
        assert result.id == user.id
        assert isinstance(result, UserReadDTO)

    async def test_create_user_already_exists(self) -> None:
        """Проверяем ошибку при создании пользователя с таким же email"""
        mock_repo = AsyncMock()
        mock_session = AsyncMock()
        user = fake_user()
        user_create_dto = UserCreateDTO(
            email=user.email,
            password=password,
        )
        mock_repo.exists.return_value = True
        service = UserService(mock_session, mock_repo)
        with pytest.raises(UserAlreadyExists):
            await service.create_user(user_create_dto)

    @pytest.mark.parametrize(
        "update_field, value",
        (
            ("email", "test2@example.com"),
            ("first_name", "Test"),
            ("last_name", "Testing"),
            ("birth_date", "1990-01-01"),
            ("is_active", False),
            ("is_superuser", True),
            ("is_verified", False),
        ),
    )
    async def test_update_user_success(self, update_field: str, value: Any) -> None:
        """Проверяем обновление пользователя"""
        mock_repo = AsyncMock()
        mock_session = AsyncMock()
        user = fake_user()
        setattr(user, update_field, value)
        user_update_dto = UserUpdateDTO(**{update_field: value})
        mock_repo.exists.return_value = True
        mock_repo.update.return_value = user
        service = UserService(mock_session, mock_repo)
        result = await service.update_user(user.id, user_update_dto)
        assert result.id == user.id
        assert isinstance(result, UserReadDTO)
        assert getattr(result, update_field) == value

    async def test_update_user_not_exists(self) -> None:
        """Проверяем ошибку при обновлении пользователя, которого нет в базе"""
        mock_repo = AsyncMock()
        mock_session = AsyncMock()
        user = fake_user()
        user_update_dto = UserCreateDTO(
            email=user.email,
            password=password,
        )
        mock_repo.exists.return_value = False
        service = UserService(mock_session, mock_repo)
        with pytest.raises(UserNotExists):
            await service.update_user(user.id, user_update_dto)

    async def test_delete_user_success(self) -> None:
        """Проверяем удаление пользователя"""
        mock_repo = AsyncMock()
        mock_session = AsyncMock()
        user = fake_user()
        mock_repo.exists.return_value = True
        mock_repo.delete.return_value = None
        service = UserService(mock_session, mock_repo)
        await service.delete_user(user.id)
        mock_repo.exists.assert_called_once_with(id=user.id)
        mock_repo.delete.assert_called_once_with(user.id)

    async def test_delete_user_not_exists(self) -> None:
        """Проверяем ошибку при удалении пользователя, которого нет в базе"""
        mock_repo = AsyncMock()
        mock_session = AsyncMock()
        user = fake_user()
        mock_repo.exists.return_value = False
        service = UserService(mock_session, mock_repo)
        with pytest.raises(UserNotExists):
            await service.delete_user(user.id)
        mock_repo.exists.assert_called_once_with(id=user.id)
