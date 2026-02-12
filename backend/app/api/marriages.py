"""
Marriage API endpoints.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.marriage import MarriageCreate, MarriageResponse, MarriageEnd
from app.services.marriage import MarriageService

router = APIRouter(prefix="/marriages", tags=["marriages"])


@router.post("", response_model=MarriageResponse)
async def create_marriage(
    data: MarriageCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new marriage (start)."""
    service = MarriageService(db)
    marriage = await service.create_marriage(
        person_a_id=data.person_a_id,
        person_b_id=data.person_b_id,
        start_date=data.start_date,
    )
    await db.commit()
    await db.refresh(marriage)
    return marriage


@router.post("/{marriage_id}/end", response_model=MarriageResponse)
async def end_marriage(
    marriage_id: uuid.UUID,
    data: MarriageEnd,
    db: AsyncSession = Depends(get_db),
):
    """End a marriage (divorce/widowed)."""
    service = MarriageService(db)
    marriage = await service.end_marriage(
        marriage_id,
        end_date=data.end_date,
        status=data.status,
    )
    if not marriage:
        raise HTTPException(status_code=404, detail="Marriage not found")
    await db.commit()
    await db.refresh(marriage)
    return marriage


@router.get("/{marriage_id}", response_model=MarriageResponse)
async def get_marriage(
    marriage_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get marriage by ID."""
    service = MarriageService(db)
    marriage = await service.get_marriage(marriage_id)
    if not marriage:
        raise HTTPException(status_code=404, detail="Marriage not found")
    return marriage
