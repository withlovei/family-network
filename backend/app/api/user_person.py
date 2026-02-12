"""
User-Person mapping API endpoints.
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user_person import UserPersonLink, UserPersonActive, PersonMappingResponse
from app.models.user_person import UserPerson
from app.models.person import Person
from app.api.dependencies import get_current_user_id

router = APIRouter(prefix="/me/persons", tags=["user-person"])


@router.get("", response_model=list[PersonMappingResponse])
async def list_user_persons(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List persons mapped to current user."""
    user_uuid = uuid.UUID(user_id)
    result = await db.execute(
        select(UserPerson.person_id).where(UserPerson.user_id == user_uuid)
    )
    person_ids = [row[0] for row in result.all()]
    if not person_ids:
        return []

    persons = await db.execute(
        select(Person.id, Person.full_name).where(Person.id.in_(person_ids))
    )
    return [
        PersonMappingResponse(person_id=row[0], full_name=row[1]) for row in persons.all()
    ]


@router.post("/link", response_model=dict)
async def link_person(
    data: UserPersonLink,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Link a person to current user."""
    user_uuid = uuid.UUID(user_id)

    # Check if person exists
    person = await db.get(Person, data.person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    # Check if already linked
    existing = await db.execute(
        select(UserPerson).where(
            UserPerson.user_id == user_uuid,
            UserPerson.person_id == data.person_id,
        )
    )
    if existing.scalar_one_or_none():
        return {"ok": True, "message": "Already linked"}

    # Create link
    link = UserPerson(user_id=user_uuid, person_id=data.person_id)
    db.add(link)
    await db.commit()
    return {"ok": True, "message": "Person linked successfully"}


@router.post("/active", response_model=dict)
async def set_active_person(
    data: UserPersonActive,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Set active person for current user.
    TODO: Store in session/context. For Phase 1 MVP, just validate the link exists.
    """
    user_uuid = uuid.UUID(user_id)

    # Check if link exists
    link = await db.execute(
        select(UserPerson).where(
            UserPerson.user_id == user_uuid,
            UserPerson.person_id == data.person_id,
        )
    )
    if not link.scalar_one_or_none():
        raise HTTPException(
            status_code=403,
            detail="Person not linked to your account. Please link first.",
        )

    return {"ok": True, "active_person_id": str(data.person_id)}
