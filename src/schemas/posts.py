from datetime import datetime

from pydantic import BaseModel

from src.schemas.users import UserRead


class PostCreate(BaseModel):
    title: str
    content: str


class PostRead(BaseModel):
    id: int
    title: str
    content: str
    pub_date: datetime

    author: "UserRead"
