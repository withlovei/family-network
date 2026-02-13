import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user_id
from app.codes import (
    MEMBER_FORBIDDEN,
    MEMBER_LINK_USER_ALREADY_LINKED,
    MEMBER_NOT_FOUND_OR_DENIED,
)
from app.database import get_db
from app.schemas.member import MemberResponse, MemberUpdate, MemberLinkUser
from app.services import member as member_service

router = APIRouter(prefix="/members", tags=["members"])


@router.get("/{member_id}", response_model=MemberResponse)
async def get_member(
    member_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get a member by id. User must be in the member's family network."""
    user_uuid = uuid.UUID(user_id)
    member = await member_service.get_member(db, member_id, user_uuid)
    if not member:
        raise HTTPException(
            status_code=404,
            detail={"code": MEMBER_NOT_FOUND_OR_DENIED},
        )
    return member


@router.patch("/{member_id}", response_model=MemberResponse)
async def update_member(
    member_id: uuid.UUID,
    data: MemberUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Update member. Requires OWNER or ADMIN of the network."""
    user_uuid = uuid.UUID(user_id)
    member = await member_service.update_member(db, member_id, user_uuid, data)
    if not member:
        existing = await member_service.get_member(db, member_id, user_uuid)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail={"code": MEMBER_NOT_FOUND_OR_DENIED},
            )
        raise HTTPException(
            status_code=403,
            detail={"code": MEMBER_FORBIDDEN},
        )
    await db.commit()
    return member


@router.patch("/{member_id}/remove")
async def remove_member(
    member_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Soft-remove member (set status REMOVED). Requires OWNER or ADMIN."""
    user_uuid = uuid.UUID(user_id)
    ok = await member_service.remove_member(db, member_id, user_uuid)
    if not ok:
        existing = await member_service.get_member(db, member_id, user_uuid)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail={"code": MEMBER_NOT_FOUND_OR_DENIED},
            )
        raise HTTPException(
            status_code=403,
            detail={"code": MEMBER_FORBIDDEN},
        )
    await db.commit()
    return {"code": "member.removed"}


@router.post("/{member_id}/link", response_model=MemberResponse)
async def link_member_to_user(
    member_id: uuid.UUID,
    data: MemberLinkUser,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Link member to a user account. Requires OWNER or ADMIN. One user per network."""
    user_uuid = uuid.UUID(user_id)
    member, err = await member_service.link_member_to_user(
        db, member_id, user_uuid, data.user_id
    )
    if err == "not_found":
        raise HTTPException(
            status_code=404,
            detail={"code": MEMBER_NOT_FOUND_OR_DENIED},
        )
    if err == "forbidden":
        raise HTTPException(
            status_code=403,
            detail={"code": MEMBER_FORBIDDEN},
        )
    if err == "already_linked":
        raise HTTPException(
            status_code=409,
            detail={"code": MEMBER_LINK_USER_ALREADY_LINKED},
        )
    await db.commit()
    return member


@router.delete("/{member_id}/link", response_model=MemberResponse)
async def unlink_member_user(
    member_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Clear linked user from member. Requires OWNER or ADMIN."""
    user_uuid = uuid.UUID(user_id)
    member = await member_service.unlink_member_user(db, member_id, user_uuid)
    if not member:
        existing = await member_service.get_member(db, member_id, user_uuid)
        if not existing:
            raise HTTPException(
                status_code=404,
                detail={"code": MEMBER_NOT_FOUND_OR_DENIED},
            )
        raise HTTPException(
            status_code=403,
            detail={"code": MEMBER_FORBIDDEN},
        )
    await db.commit()
    return member
