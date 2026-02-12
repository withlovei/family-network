"""
Person API endpoints.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.person import PersonCreate, PersonResponse, PersonUpdate
from app.services.person import PersonService
from app.api.dependencies import get_active_person_id

router = APIRouter(prefix="/persons", tags=["persons"])


@router.post("", response_model=PersonResponse)
async def create_person(
    data: PersonCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new person."""
    service = PersonService(db)
    person = await service.create_person(
        full_name=data.full_name,
        gender=data.gender,
        birth_date=data.birth_date,
        death_date=data.death_date,
        primary_lineage_id=data.primary_lineage_id,
    )
    await db.commit()
    await db.refresh(person)
    return person


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(
    person_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    active_person_id: uuid.UUID | None = Depends(get_active_person_id),
):
    """Get person by ID (with access check)."""
    service = PersonService(db)
    viewer_id = active_person_id
    if not viewer_id:
        raise HTTPException(
            status_code=403,
            detail="No active person. Please link a person first.",
        )
    person = await service.get_person(person_id, viewer_person_id=viewer_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found or access denied")
    return person


@router.patch("/{person_id}", response_model=PersonResponse)
async def update_person(
    person_id: uuid.UUID,
    data: PersonUpdate,
    db: AsyncSession = Depends(get_db),
    active_person_id: uuid.UUID | None = Depends(get_active_person_id),
):
    """Update person (requires viewer to have view access)."""
    if not active_person_id:
        raise HTTPException(
            status_code=403,
            detail="No active person. Please link a person first.",
        )
    service = PersonService(db)
    person = await service.update_person(
        person_id,
        full_name=data.full_name,
        gender=data.gender,
        birth_date=data.birth_date,
        death_date=data.death_date,
        primary_lineage_id=data.primary_lineage_id,
    )
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    await db.commit()
    await db.refresh(person)
    return person


@router.get("", response_model=list[PersonResponse])
async def list_persons(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, le=200),
    offset: int = Query(0, ge=0),
    active_person_id: uuid.UUID | None = Depends(get_active_person_id),
):
    """List persons (with access check)."""
    if not active_person_id:
        raise HTTPException(
            status_code=403,
            detail="No active person. Please link a person first.",
        )
    service = PersonService(db)
    persons = await service.list_persons(active_person_id, limit=limit, offset=offset)
    return persons
