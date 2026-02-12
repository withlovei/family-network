"""
Lineage API endpoints.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.lineage import LineageCreate, LineageResponse
from app.services.lineage import LineageService

router = APIRouter(prefix="/lineages", tags=["lineages"])


@router.post("", response_model=LineageResponse)
async def create_lineage(
    data: LineageCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new lineage."""
    service = LineageService(db)
    lineage = await service.create_lineage(
        name=data.name,
        root_person_id=data.root_person_id,
        tradition_type=data.tradition_type,
    )
    await db.commit()
    await db.refresh(lineage)
    return lineage


@router.get("", response_model=list[LineageResponse])
async def list_lineages(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, le=200),
    offset: int = Query(0, ge=0),
):
    """List lineages."""
    service = LineageService(db)
    lineages = await service.list_lineages(limit=limit, offset=offset)
    return lineages


@router.get("/{lineage_id}", response_model=LineageResponse)
async def get_lineage(
    lineage_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get lineage by ID."""
    service = LineageService(db)
    lineage = await service.get_lineage(lineage_id)
    if not lineage:
        raise HTTPException(status_code=404, detail="Lineage not found")
    return lineage
