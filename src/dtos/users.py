from dataclasses import dataclass
from datetime import date, datetime
from typing import Any


class ToDictMixin:
    def to_dict(self) -> dict[str, Any]:
        return {
            field: value for field, value in self.__dict__.items() if value is not None
        }


@dataclass
class UserCreateDTO:
    email: str
    password: str


@dataclass
class UserUpdateDTO:
    email: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None


@dataclass
class UserReadDTO:
    id: int
    email: str
    created_at: datetime
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
