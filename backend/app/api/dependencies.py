"""
Dependencies for API routes.
"""
import uuid
from fastapi import Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user_person import UserPerson


async def get_current_user_id(request: Request) -> str:
    """Get current user ID from request state (set by AuthMiddleware)."""
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id


async def get_active_person_id(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
) -> uuid.UUID | None:
    """
    Get active person_id for current user.
    For Phase 1 MVP: return first linked person, or None.
    TODO: Store active person in session/context for better UX.
    """
    user_uuid = uuid.UUID(user_id)
    result = await db.execute(
        select(UserPerson.person_id).where(UserPerson.user_id == user_uuid).limit(1)
    )
    person_id = result.scalar_one_or_none()
    return person_id
