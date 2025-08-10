from typing import Any
from unittest.mock import AsyncMock

import pytest
from fastapi import status
from httpx import AsyncClient
from tests.utils.fake_user import fake_user

from src.exceptions.users import UserNotExists


@pytest.mark.unit
class TestInitUserAPI:
    """Unit-тесты для API пользователей"""

    async def test_get_users(
        self, superuser_client: AsyncClient, mock_user_service: AsyncMock
    ) -> None:
        """Проверяем получение списка пользователей"""
        fake_users = [fake_user()]
        mock_user_service.get_users.return_value = fake_users

        response = await superuser_client.get("/users/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()[0]["id"] == fake_users[0].id
        mock_user_service.get_users.assert_called_once_with()

    async def test_get_users_return_empty_list(
        self, superuser_client: AsyncClient, mock_user_service: AsyncMock
    ) -> None:
        """Проверяем получение пустого списка пользователей"""
        mock_user_service.get_users.return_value = []

        response = await superuser_client.get("/users/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []
        mock_user_service.get_users.assert_called_once_with()

    async def test_get_me(self, authorized_user: AsyncClient) -> None:
        """Проверяем получение текущего пользователя"""
        response = await authorized_user.get("/users/me")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["email"] == fake_user().email

    @pytest.mark.parametrize(
        "upd_field, value",
        (
            ("email", "test2@example.com"),
            ("first_name", "Test"),
            ("last_name", "Testing"),
            ("birth_date", "1990-01-01"),
            ("is_active", False),
            ("is_superuser", True),
            ("is_verified", True),
        ),
    )
    async def test_update_me(
        self,
        authorized_user: AsyncClient,
        mock_user_service: AsyncMock,
        upd_field: str,
        value: Any,
    ) -> None:
        """Проверяем обновление текущего пользователя"""
        update_user = fake_user()
        setattr(update_user, upd_field, value)
        mock_user_service.update_user.return_value = update_user
        response = await authorized_user.patch("/users/me", json={upd_field: value})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()[upd_field] == value
        mock_user_service.update_user.assert_called_once()

    @pytest.mark.parametrize(
        "upd_field, value",
        (
            ("email", "test2example.com"),
            ("first_name", 1),
            ("last_name", 1),
            ("birth_date", "1990"),
            ("is_active", "30"),
            ("is_superuser", "30"),
            ("is_verified", "30"),
        ),
    )
    async def test_update_me_with_invalid_data(
        self, authorized_user: AsyncClient, upd_field: str, value: Any
    ) -> None:
        """Проверяем ошибку при обновлении текущего пользователя с неверными данными"""
        response = await authorized_user.patch("/users/me", json={upd_field: value})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_delete(
        self, superuser_client: AsyncClient, mock_user_service: AsyncMock
    ) -> None:
        """Проверяем удаление пользователя"""
        user_id = fake_user().id
        mock_user_service.delete_user.return_value = None
        response = await superuser_client.delete(f"/users/{user_id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_user_service.delete_user.assert_called_once_with(user_id)

    async def test_delete_not_exists(
        self, superuser_client: AsyncClient, mock_user_service: AsyncMock
    ) -> None:
        """Проверяем ошибку при удалении пользователя, которого нет в базе"""
        mock_user_service.delete_user.side_effect = UserNotExists()
        response = await superuser_client.delete("/users/1")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        mock_user_service.delete_user.assert_called_once_with(1)

    async def test_get_user(
        self, superuser_client: AsyncClient, mock_user_service: AsyncMock
    ) -> None:
        """Проверяем получение одного пользователя по его id"""
        user = fake_user()
        mock_user_service.get_user.return_value = user
        response = await superuser_client.get(f"/users/{user.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == user.id
        mock_user_service.get_user.assert_called_once_with(user.id)

    async def test_get_user_not_exists(
        self, superuser_client: AsyncClient, mock_user_service: AsyncMock
    ) -> None:
        """Проверяем ошибку при получении пользователя, которого нет в базе"""
        mock_user_service.get_user.side_effect = UserNotExists()
        response = await superuser_client.get("/users/1")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        "upd_field, value",
        (
            ("email", "test2@example.com"),
            ("first_name", "Test"),
            ("last_name", "Testing"),
            ("birth_date", "1990-01-01"),
            ("is_active", False),
            ("is_superuser", True),
            ("is_verified", True),
        ),
    )
    async def test_update_user(
        self,
        superuser_client: AsyncClient,
        mock_user_service: AsyncMock,
        upd_field: str,
        value: Any,
    ) -> None:
        """Проверяем обновление одного пользователя по его id"""
        user = fake_user()
        setattr(user, upd_field, value)
        mock_user_service.update_user.return_value = user
        response = await superuser_client.patch(
            f"/users/{user.id}", json={upd_field: value}
        )
        assert response.status_code == status.HTTP_200_OK
        mock_user_service.update_user.assert_called_once()

    @pytest.mark.parametrize(
        "upd_field, value",
        (
            ("email", "test2example.com"),
            ("first_name", 1),
            ("last_name", 1),
            ("birth_date", "1990"),
            ("is_active", "30"),
            ("is_superuser", "30"),
            ("is_verified", "30"),
        ),
    )
    async def test_update_user_with_invalid_data(
        self, superuser_client: AsyncClient, upd_field: str, value: Any
    ) -> None:
        """
        Проверяем ошибку при обновлении одного пользователя по его id с
        неверными данными
        """
        user = fake_user()
        setattr(user, upd_field, value)
        response = await superuser_client.patch(
            f"/users/{user.id}", json={upd_field: value}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_user(
        self, unauthenticated_client: AsyncClient, mock_user_service: AsyncMock
    ) -> None:
        """Проверяем создание нового пользователя"""
        user = fake_user()
        create_data = {"email": user.email, "password": "test"}
        mock_user_service.create_user.return_value = user
        response = await unauthenticated_client.post(
            "/users/register",
            json=create_data,
        )
        assert response.status_code == status.HTTP_201_CREATED
        mock_user_service.create_user.assert_called_once()

    @pytest.mark.parametrize(
        "field, value", (("email", "invalid_email"), ("password", 1))
    )
    async def test_create_user_with_invalid_data(
        self, unauthenticated_client: AsyncClient, field: str, value: Any
    ) -> None:
        """Проверяем ошибку при создании пользователя с неверными данными"""
        user = fake_user()
        create_data = {"email": user.email, "password": "test"}
        create_data[field] = value
        response = await unauthenticated_client.post(
            "/users/register", json=create_data
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize(
        "url, method",
        (
            ("/users/", "get"),
            ("/users/me", "get"),
            ("/users/me", "patch"),
            ("/users/1", "get"),
            ("/users/1", "patch"),
            ("/users/1", "delete"),
        ),
    )
    async def test_access_for_unauthenticated_user(
        self, unauthenticated_client: AsyncClient, url: str, method: str
    ) -> None:
        """Проверяем доступ для неавторизованных пользователей"""
        response = await getattr(unauthenticated_client, method)(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        "url, method",
        (
            ("/users/", "get"),
            ("/users/1", "get"),
            ("/users/1", "patch"),
            ("/users/1", "delete"),
        ),
    )
    async def test_access_for_not_superuser(
        self, authorized_user: AsyncClient, url: str, method: str
    ) -> None:
        """Проверяем доступ для пользователей с статусом `is_superuser=False`"""
        response = await getattr(authorized_user, method)(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
