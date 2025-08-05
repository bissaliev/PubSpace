from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_db
from src.managers.post_manager import PostManager
from src.schemas.posts import PostCreate, PostRead

router = APIRouter()


@router.get("/", response_model=list[PostRead])
async def read_posts(
    db: Annotated[AsyncSession, Depends(get_db)], email: str | None = None
):
    manager = PostManager(db)
    return await manager.get_posts(email=email)


@router.post("/", response_model=PostRead)
async def create_post(
    post: PostCreate,
    author_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    manager = PostManager(db)
    return await manager.create_post_orm(post, author_id=author_id)


@router.get("/{id}", response_model=PostRead)
async def read_post(id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    manager = PostManager(db)
    return await manager.get_post(id)


@router.delete("/{id}", status_code=204)
async def delete_post(id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    manager = PostManager(db)
    return await manager.delete_post_orm(id)


@router.delete("/{id}", status_code=204)
async def delete_post_author(
    id: int, author_id: int, db: Annotated[AsyncSession, Depends(get_db)]
):
    manager = PostManager(db)
    return await manager.delete_post_author(id, author_id)
