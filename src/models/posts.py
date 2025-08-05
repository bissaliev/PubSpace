from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.users import User


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    title: Mapped[str] = mapped_column(String(150), index=True)
    content: Mapped[str] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    pub_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    author: Mapped[list["User"]] = relationship("User", back_populates="posts")
