import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user_id
from app.codes import (
    NETWORK_FORBIDDEN,
    NETWORK_NOT_FOUND_OR_DENIED,
    NETWORK_MEMBER_USER_NOT_FOUND,
    NETWORK_MEMBER_ALREADY_IN_NETWORK,
    NETWORK_MEMBER_FORBIDDEN,
    NETWORK_MEMBER_CANNOT_CHANGE_OWNER,
    NETWORK_MEMBER_CANNOT_REMOVE_OWNER,
    NETWORK_MEMBER_REMOVED,
)
from app.database import get_db
from app.schemas.network import (
    NetworkCreate,
    NetworkUpdate,
    NetworkResponse,
    NetworkWithRoleResponse,
    NetworkMemberAdd,
    NetworkMemberUpdate,
    NetworkMemberResponse,
)
from app.schemas.family import FamilyCreate, FamilyResponse
from app.schemas.marriage import MarriageResponse
from app.schemas.member import MemberResponse
from app.services import network as network_service
from app.services import family as family_service
from app.services import member as member_service
from app.services import marriage as marriage_service

router = APIRouter(prefix="/networks", tags=["networks"])


@router.post("", response_model=NetworkResponse)
async def create_network(
    data: NetworkCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Create a new family network. Caller becomes OWNER."""
    user_uuid = uuid.UUID(user_id)
    network = await network_service.create_network(db, user_uuid, data)
    await db.commit()
    return network


@router.get("", response_model=list[NetworkWithRoleResponse])
async def list_networks(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List networks the current user is a member of."""
    user_uuid = uuid.UUID(user_id)
    rows = await network_service.list_networks_for_user(db, user_uuid)
    result = []
    for net, my_role in rows:
        result.append(
            NetworkWithRoleResponse(
                id=net.id,
                name=net.name,
                description=net.description,
                created_by=net.created_by,
                status=net.status,
                created_at=net.created_at,
                updated_at=net.updated_at,
                my_role=my_role,
            )
        )
    return result


@router.get("/{network_id}", response_model=NetworkWithRoleResponse)
async def get_network(
    network_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get a network by id. User must be a member."""
    user_uuid = uuid.UUID(user_id)
    pair = await network_service.get_network(db, network_id, user_uuid)
    if not pair:
        raise HTTPException(
            status_code=404,
            detail={"code": NETWORK_NOT_FOUND_OR_DENIED},
        )
    net, my_role = pair
    return NetworkWithRoleResponse(
        id=net.id,
        name=net.name,
        description=net.description,
        created_by=net.created_by,
        status=net.status,
        created_at=net.created_at,
        updated_at=net.updated_at,
        my_role=my_role,
    )


@router.patch("/{network_id}", response_model=NetworkResponse)
async def update_network(
    network_id: uuid.UUID,
    data: NetworkUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Update network. Requires OWNER or ADMIN."""
    user_uuid = uuid.UUID(user_id)
    network = await network_service.update_network(db, network_id, user_uuid, data)
    if not network:
        pair = await network_service.get_network(db, network_id, user_uuid)
        if not pair:
            raise HTTPException(
                status_code=404,
                detail={"code": NETWORK_NOT_FOUND_OR_DENIED},
            )
        raise HTTPException(
            status_code=403,
            detail={"code": NETWORK_FORBIDDEN},
        )
    await db.commit()
    return network


@router.patch("/{network_id}/archive", response_model=NetworkResponse)
async def archive_network(
    network_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Soft-delete network (set status ARCHIVED). Only OWNER."""
    user_uuid = uuid.UUID(user_id)
    network = await network_service.archive_network(db, network_id, user_uuid)
    if not network:
        pair = await network_service.get_network(db, network_id, user_uuid)
        if not pair:
            raise HTTPException(
                status_code=404,
                detail={"code": NETWORK_NOT_FOUND_OR_DENIED},
            )
        raise HTTPException(
            status_code=403,
            detail={"code": NETWORK_FORBIDDEN},
        )
    await db.commit()
    return network


# --- Families (in network) ---


@router.get("/{network_id}/families", response_model=list[FamilyResponse])
async def list_network_families(
    network_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List families in the network. User must be a member."""
    user_uuid = uuid.UUID(user_id)
    families = await family_service.list_families_for_network(db, network_id, user_uuid)
    if families is None:
        raise HTTPException(
            status_code=404,
            detail={"code": NETWORK_NOT_FOUND_OR_DENIED},
        )
    return families


@router.post("/{network_id}/families", response_model=FamilyResponse)
async def create_family(
    network_id: uuid.UUID,
    data: FamilyCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Create a family in the network. Requires OWNER or ADMIN."""
    user_uuid = uuid.UUID(user_id)
    family = await family_service.create_family(db, network_id, user_uuid, data)
    if not family:
        pair = await network_service.get_network(db, network_id, user_uuid)
        if not pair:
            raise HTTPException(
                status_code=404,
                detail={"code": NETWORK_NOT_FOUND_OR_DENIED},
            )
        raise HTTPException(
            status_code=403,
            detail={"code": NETWORK_FORBIDDEN},
        )
    await db.commit()
    return family


# --- Network members (RBAC) ---


@router.get("/{network_id}/members", response_model=list[NetworkMemberResponse])
async def list_network_members(
    network_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List members of the network. Caller must be a member (any role)."""
    user_uuid = uuid.UUID(user_id)
    members = await network_service.list_network_members(db, network_id, user_uuid)
    if members is None:
        raise HTTPException(
            status_code=404,
            detail={"code": NETWORK_NOT_FOUND_OR_DENIED},
        )
    return [NetworkMemberResponse(**m) for m in members]


@router.post("/{network_id}/members", response_model=NetworkMemberResponse)
async def add_network_member(
    network_id: uuid.UUID,
    data: NetworkMemberAdd,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Add a user to the network by email. Requires OWNER or ADMIN."""
    user_uuid = uuid.UUID(user_id)
    member, err = await network_service.add_member_by_email(db, network_id, user_uuid, data)
    if err == "user_not_found":
        raise HTTPException(
            status_code=404,
            detail={"code": NETWORK_MEMBER_USER_NOT_FOUND},
        )
    if err == "already_in_network":
        raise HTTPException(
            status_code=409,
            detail={"code": NETWORK_MEMBER_ALREADY_IN_NETWORK},
        )
    if member is None:
        raise HTTPException(
            status_code=403,
            detail={"code": NETWORK_MEMBER_FORBIDDEN},
        )
    await db.commit()
    return NetworkMemberResponse(**member)


@router.patch("/{network_id}/members/{member_user_id}", response_model=NetworkMemberResponse)
async def update_network_member(
    network_id: uuid.UUID,
    member_user_id: uuid.UUID,
    data: NetworkMemberUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Update a member's role. Requires OWNER or ADMIN. Cannot change OWNER."""
    user_uuid = uuid.UUID(user_id)
    member, err = await network_service.update_member_role(
        db, network_id, member_user_id, user_uuid, data
    )
    if err == "forbidden":
        raise HTTPException(
            status_code=403,
            detail={"code": NETWORK_MEMBER_FORBIDDEN},
        )
    if err == "not_found":
        raise HTTPException(
            status_code=404,
            detail={"code": NETWORK_NOT_FOUND_OR_DENIED},
        )
    if err == "cannot_change_owner":
        raise HTTPException(
            status_code=400,
            detail={"code": NETWORK_MEMBER_CANNOT_CHANGE_OWNER},
        )
    if member is None:
        raise HTTPException(
            status_code=404,
            detail={"code": NETWORK_NOT_FOUND_OR_DENIED},
        )
    await db.commit()
    return NetworkMemberResponse(**member)


@router.delete("/{network_id}/members/{member_user_id}")
async def remove_network_member(
    network_id: uuid.UUID,
    member_user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Remove a member from the network (set status REMOVED). Requires OWNER or ADMIN. Cannot remove OWNER."""
    user_uuid = uuid.UUID(user_id)
    ok, err = await network_service.remove_member(db, network_id, member_user_id, user_uuid)
    if err == "forbidden":
        raise HTTPException(
            status_code=403,
            detail={"code": NETWORK_MEMBER_FORBIDDEN},
        )
    if err == "not_found":
        raise HTTPException(
            status_code=404,
            detail={"code": NETWORK_NOT_FOUND_OR_DENIED},
        )
    if err == "cannot_remove_owner":
        raise HTTPException(
            status_code=400,
            detail={"code": NETWORK_MEMBER_CANNOT_REMOVE_OWNER},
        )
    if not ok:
        raise HTTPException(
            status_code=404,
            detail={"code": NETWORK_NOT_FOUND_OR_DENIED},
        )
    await db.commit()
    return {"code": NETWORK_MEMBER_REMOVED}


# --- Family members in network (for marriage form, etc.) ---


@router.get("/{network_id}/family-members", response_model=list[MemberResponse])
async def list_network_family_members(
    network_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List all family members (Member) in the network. User must be in network."""
    user_uuid = uuid.UUID(user_id)
    members = await member_service.list_members_in_network(db, network_id, user_uuid)
    if members is None:
        raise HTTPException(
            status_code=404,
            detail={"code": NETWORK_NOT_FOUND_OR_DENIED},
        )
    return members


@router.get("/{network_id}/marriages", response_model=list[MarriageResponse])
async def list_network_marriages(
    network_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List marriages in the network. User must be in network."""
    user_uuid = uuid.UUID(user_id)
    marriages = await marriage_service.list_marriages_for_network(db, network_id, user_uuid)
    if marriages is None:
        raise HTTPException(
            status_code=404,
            detail={"code": NETWORK_NOT_FOUND_OR_DENIED},
        )
    return marriages
