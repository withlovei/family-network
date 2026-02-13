import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user_id
from app.codes import (
    MARRIAGE_NOT_FOUND_OR_DENIED,
    MARRIAGE_SAME_MEMBER,
    MARRIAGE_DIFFERENT_NETWORK,
    MARRIAGE_ALREADY_ACTIVE,
    MARRIAGE_FORBIDDEN,
)
from app.database import get_db
from app.schemas.marriage import MarriageCreate, MarriageUpdate, MarriageResponse
from app.services import marriage as marriage_service

router = APIRouter(prefix="/marriages", tags=["marriages"])


@router.post("", response_model=MarriageResponse)
async def create_marriage(
    data: MarriageCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Create a marriage between two members. Requires OWNER or ADMIN in the network."""
    user_uuid = uuid.UUID(user_id)
    marriage, err = await marriage_service.create_marriage(db, user_uuid, data)
    if err == "same_member":
        raise HTTPException(status_code=400, detail={"code": MARRIAGE_SAME_MEMBER})
    if err == "different_network":
        raise HTTPException(status_code=400, detail={"code": MARRIAGE_DIFFERENT_NETWORK})
    if err == "already_active":
        raise HTTPException(status_code=409, detail={"code": MARRIAGE_ALREADY_ACTIVE})
    if err == "forbidden":
        raise HTTPException(status_code=403, detail={"code": MARRIAGE_FORBIDDEN})
    if err == "not_found":
        raise HTTPException(status_code=404, detail={"code": MARRIAGE_NOT_FOUND_OR_DENIED})
    if marriage is None:
        raise HTTPException(status_code=404, detail={"code": MARRIAGE_NOT_FOUND_OR_DENIED})
    await db.commit()
    return marriage


@router.get("/{marriage_id}", response_model=MarriageResponse)
async def get_marriage(
    marriage_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get a marriage by id. User must be in the same network."""
    user_uuid = uuid.UUID(user_id)
    marriage = await marriage_service.get_marriage(db, marriage_id, user_uuid)
    if not marriage:
        raise HTTPException(
            status_code=404,
            detail={"code": MARRIAGE_NOT_FOUND_OR_DENIED},
        )
    return marriage


@router.patch("/{marriage_id}", response_model=MarriageResponse)
async def update_marriage(
    marriage_id: uuid.UUID,
    data: MarriageUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Update marriage status (e.g. DIVORCED, ENDED). Requires OWNER or ADMIN."""
    user_uuid = uuid.UUID(user_id)
    marriage = await marriage_service.update_marriage(db, marriage_id, user_uuid, data)
    if not marriage:
        existing = await marriage_service.get_marriage(db, marriage_id, user_uuid)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail={"code": MARRIAGE_NOT_FOUND_OR_DENIED},
            )
        raise HTTPException(
            status_code=403,
            detail={"code": MARRIAGE_FORBIDDEN},
        )
    await db.commit()
    return marriage
