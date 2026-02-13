import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.family_network import (
    Family,
    NetworkUserRole,
    NetworkRole,
    NetworkUserRoleStatus,
)
from app.models.member import Member, MemberGender, MemberStatus, MemberFamilyRole
from app.schemas.member import MemberCreate, MemberUpdate
from app.services.network import get_user_role_in_network


def _require_owner_or_admin(role: NetworkUserRole | None) -> bool:
    return role is not None and role.role in (NetworkRole.OWNER, NetworkRole.ADMIN)


async def _get_family_network_id(db: AsyncSession, family_id: uuid.UUID) -> uuid.UUID | None:
    family = await db.get(Family, family_id)
    return family.network_id if family else None


async def create_member(
    db: AsyncSession,
    family_id: uuid.UUID,
    user_id: uuid.UUID,
    data: MemberCreate,
) -> Member | None:
    """Create a member in the family. Caller must be OWNER or ADMIN of the network."""
    family = await db.get(Family, family_id)
    if not family:
        return None
    role = await get_user_role_in_network(db, family.network_id, user_id)
    if not _require_owner_or_admin(role):
        return None
    member = Member(
        family_id=family_id,
        full_name=data.full_name,
        gender=data.gender,
        family_role=data.family_role,
        date_of_birth=data.date_of_birth,
        is_alive=data.is_alive,
        status=MemberStatus.ACTIVE,
    )
    db.add(member)
    await db.flush()
    await db.refresh(member)
    return member


async def list_members_for_family(
    db: AsyncSession,
    family_id: uuid.UUID,
    user_id: uuid.UUID,
) -> list[Member] | None:
    """List active members of the family. User must be a member of the family's network."""
    family = await db.get(Family, family_id)
    if not family:
        return None
    if await get_user_role_in_network(db, family.network_id, user_id) is None:
        return None
    result = await db.execute(
        select(Member).where(
            Member.family_id == family_id,
            Member.status == MemberStatus.ACTIVE,
        ).order_by(Member.created_at.asc())
    )
    return list(result.scalars().all())


async def list_members_in_network(
    db: AsyncSession,
    network_id: uuid.UUID,
    user_id: uuid.UUID,
) -> list[Member] | None:
    """List all active family members (Member) in the network. User must be in network."""
    if await get_user_role_in_network(db, network_id, user_id) is None:
        return None
    result = await db.execute(
        select(Member)
        .join(Family, Member.family_id == Family.id)
        .where(
            Family.network_id == network_id,
            Member.status == MemberStatus.ACTIVE,
        )
        .order_by(Member.full_name)
    )
    return list(result.scalars().unique().all())


async def get_member(
    db: AsyncSession,
    member_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Member | None:
    """Get member by id. User must be in the member's family network."""
    member = await db.get(Member, member_id)
    if not member:
        return None
    family = await db.get(Family, member.family_id)
    if not family or await get_user_role_in_network(db, family.network_id, user_id) is None:
        return None
    return member


async def update_member(
    db: AsyncSession,
    member_id: uuid.UUID,
    user_id: uuid.UUID,
    data: MemberUpdate,
) -> Member | None:
    """Update member. Caller must be OWNER or ADMIN of the network."""
    member = await db.get(Member, member_id)
    if not member:
        return None
    family = await db.get(Family, member.family_id)
    if not family:
        return None
    role = await get_user_role_in_network(db, family.network_id, user_id)
    if not _require_owner_or_admin(role):
        return None
    if data.full_name is not None:
        member.full_name = data.full_name
    if data.gender is not None:
        member.gender = data.gender
    if data.family_role is not None:
        member.family_role = data.family_role
    if data.date_of_birth is not None:
        member.date_of_birth = data.date_of_birth
    if data.is_alive is not None:
        member.is_alive = data.is_alive
    await db.flush()
    await db.refresh(member)
    return member


async def remove_member(
    db: AsyncSession,
    member_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    """Set member status to REMOVED. Caller must be OWNER or ADMIN."""
    member = await db.get(Member, member_id)
    if not member:
        return False
    family = await db.get(Family, member.family_id)
    if not family:
        return False
    role = await get_user_role_in_network(db, family.network_id, user_id)
    if not _require_owner_or_admin(role):
        return False
    member.status = MemberStatus.REMOVED
    await db.flush()
    return True


async def link_member_to_user(
    db: AsyncSession,
    member_id: uuid.UUID,
    user_id: uuid.UUID,
    target_user_id: uuid.UUID,
) -> tuple[Member | None, str | None]:
    """Link member to a user. Returns (member, None) or (None, 'forbidden'|'not_found'|'already_linked')."""
    member = await db.get(Member, member_id)
    if not member:
        return (None, "not_found")
    family = await db.get(Family, member.family_id)
    if not family:
        return (None, "not_found")
    role = await get_user_role_in_network(db, family.network_id, user_id)
    if not _require_owner_or_admin(role):
        return (None, "forbidden")
    network_id = family.network_id
    result = await db.execute(
        select(Member).join(Family, Member.family_id == Family.id).where(
            Family.network_id == network_id,
            Member.linked_user_id == target_user_id,
            Member.id != member_id,
            Member.status == MemberStatus.ACTIVE,
        )
    )
    if result.scalar_one_or_none():
        return (None, "already_linked")
    member.linked_user_id = target_user_id
    await db.flush()
    await db.refresh(member)
    return (member, None)


async def unlink_member_user(
    db: AsyncSession,
    member_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Member | None:
    """Clear linked_user_id. Caller must be OWNER or ADMIN."""
    member = await db.get(Member, member_id)
    if not member:
        return None
    family = await db.get(Family, member.family_id)
    if not family:
        return None
    role = await get_user_role_in_network(db, family.network_id, user_id)
    if not _require_owner_or_admin(role):
        return None
    member.linked_user_id = None
    await db.flush()
    await db.refresh(member)
    return member
