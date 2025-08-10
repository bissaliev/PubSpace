from typing import Any

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User
from src.repositories.user_repo import UserRepository


@pytest.mark.integration
class TestUserAPI:
    """Интеграционные тесты для API пользователей"""

    async def test_create_user(
        self, async_client: AsyncClient, db_session: AsyncSession
    ) -> None:
        """Проверяем создание нового пользователя"""
        data = {"email": "test@example.com", "password": "testpassword"}
        response = await async_client.post("/users/register", json=data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["email"] == data["email"]

        repo = UserRepository(db_session)
        user = await repo.get_by_email(data["email"])
        assert user.email == data["email"]

    @pytest.mark.parametrize(
        "field, value", (("email", "invalid_email"), ("password", 1))
    )
    async def test_create_user_with_invalid_data(
        self,
        async_client: AsyncClient,
        field: str,
        value: Any,
    ) -> None:
        """Проверяем ошибку при создании пользователя с неверными данными"""
        data = {"email": "test@example.com", "password": "testpassword"}
        data[field] = value
        response = await async_client.post("/users/register", json=data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_create_user_with_existing_email(
        self, async_client: AsyncClient, user_db: User
    ) -> None:
        """Проверяем ошибку при создании пользователя с существующим email"""
        data = {"email": user_db.email, "password": "testpassword"}
        response = await async_client.post("/users/register", json=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_get_users(
        self, superuser_client: AsyncClient, user_db: User
    ) -> None:
        """
        Проверяем получение списка пользователей с авторизацией под суперпользователем
        """
        response = await superuser_client.get("/users/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2
        assert [u for u in response.json() if u["id"] == user_db.id][0][
            "id"
        ] == user_db.id

    async def test_get_user(self, superuser_client: AsyncClient, user_db: User) -> None:
        """
        Проверяем получение одного пользователя по его id с авторизацией под
        суперпользователем
        """
        response = await superuser_client.get(f"/users/{user_db.id}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == user_db.id

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
        self, superuser_client: AsyncClient, user_db: User, upd_field: str, value: Any
    ) -> None:
        """
        Проверяем обновление одного пользователя по его id с авторизацией
        под суперпользователем
        """
        response = await superuser_client.patch(
            f"/users/{user_db.id}", json={upd_field: value}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == user_db.id
        assert response.json()[upd_field] == value

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
        self, superuser_client: AsyncClient, user_db: User, upd_field: str, value: Any
    ) -> None:
        """
        Проверяем ошибку при обновлении одного пользователя по его id с
        неверными данными с авторизацией под суперпользователем
        """
        response = await superuser_client.patch(
            f"/users/{user_db.id}", json={upd_field: value}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_delete_user(
        self, superuser_client: AsyncClient, user_db: User
    ) -> None:
        """Проверяем удаление пользователя с авторизацией под суперпользователем"""
        response = await superuser_client.delete(f"/users/{user_db.id}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.parametrize(
        "url, method, data",
        (
            ("/users/100", "get", None),
            ("/users/100", "patch", {"email": "update_email@test.com"}),
            ("/users/100", "delete", None),
        ),
    )
    async def test_not_exists_user(
        self, superuser_client: AsyncClient, url: str, method: str, data: Any
    ) -> None:
        """Проверяем ошибку при попытке доступа к несуществующему ресурсу"""
        if data is not None:
            response = await getattr(superuser_client, method)(url, json=data)
        else:
            response = await getattr(superuser_client, method)(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        "url, method, data",
        (
            ("/users/1", "get", None),
            ("/users/1", "patch", {"email": "update_email@test.com"}),
            ("/users/1", "delete", None),
        ),
    )
    async def test_access_for_not_superuser(
        self, async_auth_client: AsyncClient, url: str, method: str, data: Any
    ) -> None:
        """Проверяем доступ для пользователей с статусом `is_superuser=False`"""
        if data is not None:
            response = await getattr(async_auth_client, method)(url, json=data)
        else:
            response = await getattr(async_auth_client, method)(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_current_user(
        self, async_auth_client: AsyncClient, user_db: User
    ) -> None:
        """Проверяем получение текущего пользователя"""
        response = await async_auth_client.get("/users/me")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == user_db.id

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
        async_auth_client: AsyncClient,
        user_db: User,
        upd_field: str,
        value: Any,
    ) -> None:
        """Проверяем обновление текущего пользователя"""
        update_user = user_db
        setattr(update_user, upd_field, value)
        response = await async_auth_client.patch("/users/me", json={upd_field: value})
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == user_db.id
        assert response.json()[upd_field] == value

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
        self, async_auth_client: AsyncClient, user_db: User, upd_field: str, value: Any
    ) -> None:
        """Проверяем ошибку при обновлении текущего пользователя с неверными данными"""
        response = await async_auth_client.patch("/users/me", json={upd_field: value})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize(
        "url, method, data",
        (
            ("/users/", "get", None),
            ("/users/1", "get", None),
            ("/users/1", "patch", {"email": "update_email@test.com"}),
            ("/users/1", "delete", None),
            ("/users/me", "get", None),
            ("/users/me", "patch", {"email": "update_email@test.com"}),
            ("/users/me", "delete", None),
        ),
    )
    async def test_not_access_for_not_auth_user(
        self, client: AsyncClient, url: str, method: str, data: Any
    ) -> None:
        """Проверяем ошибку при попытке доступа к ресурсу без авторизации"""
        if data is not None:
            response = await getattr(client, method)(url, json=data)
        else:
            response = await getattr(client, method)(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
class TestAuthAPI:
    async def test_login(self, async_client: AsyncClient, user_db: User) -> None:
        response = await async_client.post(
            "/auth/login",
            data={"username": user_db.email, "password": "test"},
        )
        assert response.status_code == 200
