from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from tests.utils.fake_user import fake_superuser, fake_user

from src.api.dependencies import get_current_user, get_user_service
from src.main import app
from src.services.user_service import UserService


@pytest_asyncio.fixture
def mock_user_service() -> AsyncMock:
    service = AsyncMock(spec=UserService)
    return service


@pytest_asyncio.fixture
async def superuser_client(
    mock_user_service: AsyncMock,
) -> AsyncGenerator[AsyncClient, None]:
    """Клиент с авторизацией под суперпользователем"""
    from src.api.dependencies import get_user_or_404

    app.dependency_overrides[get_user_or_404] = fake_user
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    app.dependency_overrides[get_current_user] = fake_superuser

    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def unauthenticated_client(
    mock_user_service: AsyncMock,
) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def authorized_user(
    mock_user_service: AsyncMock,
) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    app.dependency_overrides[get_current_user] = fake_user
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()
