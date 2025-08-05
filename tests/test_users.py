from httpx import AsyncClient

from src.managers.user_manager import UserManager
from src.models.users import User


class TestUserAPI:
    async def test_create_user(self, async_client: AsyncClient, db_session):
        response = await async_client.post(
            "/users/register",
            json={
                "email": "test@example.com",
                "password": "testpassword",
            },
        )
        assert response.status_code == 201
        assert response.json()["email"] == "test@example.com"

        manager = UserManager(db_session)
        user = await manager.get_by_email("test@example.com")
        assert user.email == "test@example.com"

        users = await manager.list()
        assert len(users) == 1

    async def test_get_users(self, async_client: AsyncClient):
        response = await async_client.get("/users/")
        assert response.status_code == 401

    async def test_get_users_with_auth_user(
        self, async_auth_client: AsyncClient
    ):
        response = await async_auth_client.get("/users/")
        assert response.status_code == 200

    async def test_get_user(
        self, async_auth_client: AsyncClient, user_db: User
    ):
        response = await async_auth_client.get(f"/users/{user_db.id}")
        assert response.status_code == 200
        assert response.json()["email"] == user_db.email

    async def test_update_user(
        self, async_auth_client: AsyncClient, user_db: User
    ):
        update_date = {"email": "update_email@test.com"}
        response = await async_auth_client.patch(
            f"/users/{user_db.id}", json=update_date
        )
        assert response.status_code == 200
        assert response.json()["email"] == update_date["email"]

    async def test_delete_user(
        self, async_auth_client: AsyncClient, user_db: User
    ):
        response = await async_auth_client.delete(f"/users/{user_db.id}")
        assert response.status_code == 204


class TestAuthAPI:
    async def test_login(self, async_client: AsyncClient, user_db: User):
        response = await async_client.post(
            "/auth/login",
            data={"username": user_db.email, "password": "test"},
        )
        assert response.status_code == 200
