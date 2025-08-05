import uuid
from datetime import date

from pydantic import BaseModel, EmailStr


class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    is_active: bool
    is_superuser: bool
    is_verified: bool


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class SuperUserCreate(UserCreate):
    email: EmailStr
    password: str
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    is_active: bool
    is_superuser: bool
    is_verified: bool


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    is_active: bool | None = None
    is_superuser: bool | None = None
    is_verified: bool | None = None


class Token(BaseModel):
    access_token: str
    token_type: str
