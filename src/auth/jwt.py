from datetime import UTC, datetime, timedelta

import jwt
from jwt.exceptions import InvalidTokenError

from src.core.config import settings


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta if expires_delta else timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def read_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.SECRET, algorithms=[settings.ALGORITHM]
        )
        return payload
    except InvalidTokenError:
        return {}
