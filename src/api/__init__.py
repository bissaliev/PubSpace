from fastapi import APIRouter

from src.api import auth, posts, users

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(posts.router, prefix="/posts", tags=["posts"])
