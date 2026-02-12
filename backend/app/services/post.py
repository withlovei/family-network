"""
PostService - Operations for Post with AccessService checks.
"""
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post, PostVisibility
from app.services.access import AccessService


class PostService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.access = AccessService(db)

    async def create_post(
        self,
        author_person_id: uuid.UUID,
        content: str,
        visibility: PostVisibility = PostVisibility.LINEAGE_PUBLIC,
    ) -> Post:
        """Create a new post."""
        post = Post(
            author_person_id=author_person_id,
            content=content,
            visibility=visibility,
        )
        self.db.add(post)
        await self.db.flush()
        await self.db.refresh(post)
        return post

    async def get_post(
        self, post_id: uuid.UUID, viewer_person_id: uuid.UUID | None = None
    ) -> Post | None:
        """
        Get post by ID. If viewer_person_id is provided, check access.
        """
        post = await self.db.get(Post, post_id)
        if not post:
            return None

        if viewer_person_id and not await self.access.can_view_post(viewer_person_id, post_id):
            return None

        return post

    async def list_posts(
        self, viewer_person_id: uuid.UUID, limit: int = 50, offset: int = 0
    ) -> list[Post]:
        """
        List posts that viewer can access.
        """
        result = await self.db.execute(
            select(Post).order_by(Post.created_at.desc()).limit(limit).offset(offset)
        )
        all_posts = result.scalars().all()
        accessible = []
        for post in all_posts:
            if await self.access.can_view_post(viewer_person_id, post.id):
                accessible.append(post)
        return accessible
