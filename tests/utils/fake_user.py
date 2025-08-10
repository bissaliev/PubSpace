from datetime import date

from src.auth.hashing_password import PasswordHelper
from src.models.users import User

password_superuser = "admin"


def fake_superuser() -> User:
    return User(
        id=1,
        email="test_admin@example.com",
        hashed_password=PasswordHelper().hash(password_superuser),
        first_name="Superuser",
        last_name="Superuser",
        birth_date=date(2000, 1, 1),
        is_active=True,
        is_superuser=True,
        is_verified=True,
    )


password = "password123"


def fake_user() -> User:
    return User(
        id=2,
        email="test@example.com",
        hashed_password=PasswordHelper().hash(password),
        first_name="Fake",
        last_name="Fake",
        birth_date=date(2000, 1, 1),
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )
