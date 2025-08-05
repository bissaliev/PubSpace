import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.auth.hashing_password import PasswordHelper
from src.auth.jwt import create_access_token
from src.db.database import get_db
from src.main import app
from src.models.base import Base
from src.models.users import User

# Настройка тестовой базы
TEST_DATABASE_URL = (
    "postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"
)


@pytest_asyncio.fixture
async def test_engine():
    async_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with async_engine.begin() as conn:
        # Создаём все таблицы
        await conn.run_sync(Base.metadata.create_all)
    yield async_engine
    async with async_engine.begin() as conn:
        # Удаляем все таблицы после тестов
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session(test_engine):
    test_async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    async with test_async_session() as session:
        yield session
        # Очищаем данные после каждого теста
        async with test_engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(table.delete())


@pytest.fixture
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(
        transport=ASGITransport(app), base_url="http://test"
    ) as c:
        yield c
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def superuser(db_session: AsyncSession):
    admin = User(
        email="admin@admin.com",
        hashed_password="admin",
        is_superuser=True,
    )
    db_session.add(admin)
    await db_session.commit()
    yield admin


@pytest_asyncio.fixture
async def user_db(db_session: AsyncSession):
    pwd_helper = PasswordHelper()
    user = User(
        email="test_user@test.com", hashed_password=pwd_helper.hash("test")
    )
    db_session.add(user)
    await db_session.commit()
    yield user


@pytest_asyncio.fixture
async def async_auth_client(db_session: AsyncSession, superuser):
    token = create_access_token({"sub": superuser.email})
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"},
    ) as c:
        yield c
    app.dependency_overrides.clear()
