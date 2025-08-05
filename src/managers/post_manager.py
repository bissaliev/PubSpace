from sqlalchemy import delete, insert, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload, selectinload

from src.models.posts import Post
from src.models.users import User
from src.schemas.posts import PostCreate, PostRead
from src.schemas.users import UserRead


class PostManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_posts(
        self, offset: int = 0, limit: int = 100, email: str | None = None
    ) -> list[Post]:
        stmt = (
            select(Post).join(Post.author).options(contains_eager(Post.author))
        )
        if email:
            stmt = stmt.where(User.email.like(f"%{email}%"))
        stmt = stmt.limit(limit).offset(offset)
        return (await self.session.scalars(stmt)).all()

    async def create_post_orm2(
        self, post_data: PostCreate, author_id: int
    ) -> Post:
        user = (
            await self.session.scalars(
                select(User).where(User.id == author_id)
            )
        ).first()
        if user:
            raise ValueError("User not found")
        new_post = Post(**post_data.model_dump())
        new_post.author = user
        self.session.add(new_post)
        await self.session.commit()
        await self.session.refresh(new_post, ["author"])
        return new_post

    async def create_post(self, post_data: PostCreate, author_id: int) -> Post:
        user = (
            await self.session.scalars(
                select(User).where(User.id == author_id)
            )
        ).first()

        if user:
            ValueError("User not found")
        stmt = (
            insert(Post)
            .values(
                title=post_data.title,
                content=post_data.content,
                author_id=user.id,
            )
            .returning(Post.id)
        )
        post_id = (await self.session.scalars(stmt)).first()
        await self.session.commit()
        new_post = (
            await self.session.scalars(
                select(Post)
                .where(Post.id == post_id)
                .options(joinedload(Post.author))
            )
        ).first()
        return new_post

    async def create_post_orm(
        self, post_data: PostCreate, author_id: int
    ) -> Post:
        user = await self.session.get(User, author_id)
        new_post = Post(**post_data.model_dump())
        (await user.awaitable_attrs.posts).append(new_post)
        # user.posts.append(new_post)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(new_post, ["author"])
        return new_post

    async def get_post(self, id: int) -> Post:
        stmt = (
            select(Post)
            .where(Post.id == id)
            .options(selectinload(Post.author))
        )
        return (await self.session.scalars(stmt)).first()

    async def delete_post(self, id: int) -> None:
        stmt = delete(Post).where(Post.id == id)
        await self.session.execute(stmt)

    async def delete_post_orm(self, id: int) -> None:
        post = await self.session.get(Post, id)
        await self.session.delete(post)
        await self.session.commit()

    async def delete_post_author(self, id: int, author_id: int):
        user = await self.session.get(User, author_id)
        post = await self.session.get(Post, id)
        user.posts.remove(post)
        await self.session.commit()

    async def get_post_sql(self, id: int) -> Post:
        query = text("""
            SELECT
                posts.id AS post_id,
                posts.title,
                posts.content,
                posts.author_id,
                posts.pub_date,
                users.id AS user_id,
                users.email,
                users.first_name,
                users.last_name,
                users.birth_date
            FROM posts
            LEFT OUTER JOIN users ON users.id = posts.author_id
            WHERE posts.id = :id
        """)
        result = await self.session.execute(query, {"id": id})
        row = result.first()
        if row.user_id:  # Проверяем, есть ли данные автора (не NULL)
            author = UserRead(
                id=row.user_id,
                email=row.email,
                first_name=row.first_name,
                last_name=row.last_name,
                birth_date=row.birth_date,
            )

        return PostRead(
            id=row.post_id,
            title=row.title,
            content=row.content,
            pub_date=row.pub_date,
            author=author,
        )
