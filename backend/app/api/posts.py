"""
Post API endpoints.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.post import PostCreate, PostResponse
from app.services.post import PostService
from app.api.dependencies import get_active_person_id

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("", response_model=PostResponse)
async def create_post(
    data: PostCreate,
    db: AsyncSession = Depends(get_db),
    active_person_id: uuid.UUID | None = Depends(get_active_person_id),
):
    """Create a new post."""
    if not active_person_id:
        raise HTTPException(
            status_code=403,
            detail="No active person. Please link a person first.",
        )
    service = PostService(db)
    post = await service.create_post(
        author_person_id=active_person_id,
        content=data.content,
        visibility=data.visibility,
    )
    await db.commit()
    await db.refresh(post)
    return post


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    active_person_id: uuid.UUID | None = Depends(get_active_person_id),
):
    """Get post by ID (with access check)."""
    if not active_person_id:
        raise HTTPException(
            status_code=403,
            detail="No active person. Please link a person first.",
        )
    service = PostService(db)
    post = await service.get_post(post_id, viewer_person_id=active_person_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found or access denied")
    return post


@router.get("", response_model=list[PostResponse])
async def list_posts(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    active_person_id: uuid.UUID | None = Depends(get_active_person_id),
):
    """List posts (with access check)."""
    if not active_person_id:
        raise HTTPException(
            status_code=403,
            detail="No active person. Please link a person first.",
        )
    service = PostService(db)
    posts = await service.list_posts(active_person_id, limit=limit, offset=offset)
    return posts
