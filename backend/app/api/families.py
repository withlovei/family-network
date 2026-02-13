import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user_id
from app.codes import (
    FAMILY_FORBIDDEN,
    FAMILY_NOT_FOUND_OR_DENIED,
    MARRIAGE_ALREADY_ACTIVE,
    MARRIAGE_FORBIDDEN,
    MARRIAGE_MEMBER_NOT_IN_FAMILY,
)
from app.database import get_db
from app.schemas.family import FamilyResponse, FamilyUpdate
from app.schemas.marriage import (
    MarriageResponse,
    NewFamilyWithMarriageCreate,
    NewFamilyWithMarriageResponse,
)
from app.schemas.member import MemberCreate, MemberResponse
from app.services import family as family_service
from app.services import member as member_service
from app.services import marriage as marriage_service

router = APIRouter(prefix="/families", tags=["families"])


@router.get("/{family_id}", response_model=FamilyResponse)
async def get_family(
    family_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get a family by id. User must be a member of the family's network."""
    user_uuid = uuid.UUID(user_id)
    family = await family_service.get_family(db, family_id, user_uuid)
    if not family:
        raise HTTPException(
            status_code=404,
            detail={"code": FAMILY_NOT_FOUND_OR_DENIED},
        )
    return family


@router.patch("/{family_id}", response_model=FamilyResponse)
async def update_family(
    family_id: uuid.UUID,
    data: FamilyUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Update family. Requires OWNER or ADMIN of the network."""
    user_uuid = uuid.UUID(user_id)
    family = await family_service.update_family(db, family_id, user_uuid, data)
    if not family:
        existing = await family_service.get_family(db, family_id, user_uuid)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail={"code": FAMILY_NOT_FOUND_OR_DENIED},
            )
        raise HTTPException(
            status_code=403,
            detail={"code": FAMILY_FORBIDDEN},
        )
    await db.commit()
    return family


@router.patch("/{family_id}/archive", response_model=FamilyResponse)
async def archive_family(
    family_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Soft-delete family (set status ARCHIVED). Requires OWNER or ADMIN."""
    user_uuid = uuid.UUID(user_id)
    family = await family_service.archive_family(db, family_id, user_uuid)
    if not family:
        existing = await family_service.get_family(db, family_id, user_uuid)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail={"code": FAMILY_NOT_FOUND_OR_DENIED},
            )
        raise HTTPException(
            status_code=403,
            detail={"code": FAMILY_FORBIDDEN},
        )
    await db.commit()
    return family


# --- Family members ---


@router.get("/{family_id}/members", response_model=list[MemberResponse])
async def list_family_members(
    family_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List members of the family. User must be in the family's network."""
    user_uuid = uuid.UUID(user_id)
    members = await member_service.list_members_for_family(db, family_id, user_uuid)
    if members is None:
        raise HTTPException(
            status_code=404,
            detail={"code": FAMILY_NOT_FOUND_OR_DENIED},
        )
    return members


@router.post("/{family_id}/members", response_model=MemberResponse)
async def create_family_member(
    family_id: uuid.UUID,
    data: MemberCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Create a member in the family. Requires OWNER or ADMIN of the network."""
    user_uuid = uuid.UUID(user_id)
    member = await member_service.create_member(db, family_id, user_uuid, data)
    if not member:
        family = await family_service.get_family(db, family_id, user_uuid)
        if not family:
            raise HTTPException(
                status_code=404,
                detail={"code": FAMILY_NOT_FOUND_OR_DENIED},
            )
        raise HTTPException(
            status_code=403,
            detail={"code": FAMILY_FORBIDDEN},
        )
    await db.commit()
    return member


# --- New family with marriage (child + new spouse) ---


@router.post(
    "/{family_id}/new-family-with-marriage",
    response_model=NewFamilyWithMarriageResponse,
)
async def create_new_family_with_marriage(
    family_id: uuid.UUID,
    data: NewFamilyWithMarriageCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Create a new family with one member from this family (child) + new spouse; record marriage."""
    user_uuid = uuid.UUID(user_id)
    result, err = await marriage_service.create_new_family_with_marriage(
        db, family_id, user_uuid, data
    )
    if err == "not_found":
        raise HTTPException(
            status_code=404,
            detail={"code": FAMILY_NOT_FOUND_OR_DENIED},
        )
    if err == "forbidden":
        raise HTTPException(
            status_code=403,
            detail={"code": MARRIAGE_FORBIDDEN},
        )
    if err == "member_not_in_family":
        raise HTTPException(
            status_code=400,
            detail={"code": MARRIAGE_MEMBER_NOT_IN_FAMILY},
        )
    if err == "already_active":
        raise HTTPException(
            status_code=409,
            detail={"code": MARRIAGE_ALREADY_ACTIVE},
        )
    if not result:
        raise HTTPException(
            status_code=404,
            detail={"code": FAMILY_NOT_FOUND_OR_DENIED},
        )
    new_family, marriage = result
    await db.commit()
    return NewFamilyWithMarriageResponse(
        family_id=new_family.id,
        marriage_id=marriage.id,
    )


@router.get("/{family_id}/marriages", response_model=list[MarriageResponse])
async def list_family_marriages(
    family_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List marriages where at least one member belongs to this family."""
    user_uuid = uuid.UUID(user_id)
    marriages = await marriage_service.list_marriages_for_family(
        db, family_id, user_uuid
    )
    if marriages is None:
        raise HTTPException(
            status_code=404,
            detail={"code": FAMILY_NOT_FOUND_OR_DENIED},
        )
    return marriages
