import uuid
from datetime import date
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.family_network import (
    Family,
    FamilyStatus,
    NetworkUserRole,
    NetworkRole,
)
from app.models.member import Member, MemberStatus
from app.models.marriage import Marriage, MarriageStatus
from app.schemas.marriage import MarriageCreate, MarriageUpdate, NewFamilyWithMarriageCreate
from app.services.network import get_user_role_in_network


def _require_owner_or_admin(role: NetworkUserRole | None) -> bool:
    return role is not None and role.role in (NetworkRole.OWNER, NetworkRole.ADMIN)


async def _get_member_network_id(db: AsyncSession, member_id: uuid.UUID) -> uuid.UUID | None:
    """Return network_id for the member's family, or None."""
    member = await db.get(Member, member_id)
    if not member:
        return None
    family = await db.get(Family, member.family_id)
    return family.network_id if family else None


async def _has_active_marriage(db: AsyncSession, member_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(Marriage)
        .where(
            ((Marriage.member_id_1 == member_id) | (Marriage.member_id_2 == member_id)),
            Marriage.status == MarriageStatus.ACTIVE,
        )
        .limit(1)
    )
    return result.scalar_one_or_none() is not None


async def create_new_family_with_marriage(
    db: AsyncSession,
    family_id: uuid.UUID,
    user_id: uuid.UUID,
    data: NewFamilyWithMarriageCreate,
) -> tuple[tuple[Family, Marriage] | None, str | None]:
    """Create a new family with one existing member (child) + new spouse; record marriage.
    Returns ((new_family, marriage), None) or (None, error_code).
    error_code: not_found | forbidden | member_not_in_family | already_active."""
    family = await db.get(Family, family_id)
    if not family:
        return (None, "not_found")
    network_id = family.network_id
    role = await get_user_role_in_network(db, network_id, user_id)
    if not _require_owner_or_admin(role):
        return (None, "forbidden")
    member = await db.get(Member, data.member_id)
    if not member or member.family_id != family_id or member.status != MemberStatus.ACTIVE:
        return (None, "member_not_in_family")
    if await _has_active_marriage(db, data.member_id):
        return (None, "already_active")

    new_family = Family(
        network_id=network_id,
        name=f"Gia đình của {member.full_name} & {data.spouse.full_name}",
        description=None,
        created_by=user_id,
        status=FamilyStatus.ACTIVE,
    )
    db.add(new_family)
    await db.flush()

    spouse = Member(
        family_id=new_family.id,
        full_name=data.spouse.full_name,
        gender=data.spouse.gender,
        date_of_birth=data.spouse.date_of_birth,
        is_alive=data.spouse.is_alive,
        status=MemberStatus.ACTIVE,
    )
    db.add(spouse)
    await db.flush()

    member.family_id = new_family.id
    await db.flush()

    marriage = Marriage(
        member_id_1=data.member_id,
        member_id_2=spouse.id,
        marriage_date=data.marriage_date,
        status=MarriageStatus.ACTIVE,
    )
    db.add(marriage)
    await db.flush()
    await db.refresh(new_family)
    await db.refresh(marriage)
    return ((new_family, marriage), None)


async def create_marriage(
    db: AsyncSession,
    user_id: uuid.UUID,
    data: MarriageCreate,
) -> tuple[Marriage | None, str | None]:
    """Create marriage. Returns (marriage, None) or (None, error_code).
    error_code: same_member | different_network | already_active | forbidden | not_found."""
    if data.member_id_1 == data.member_id_2:
        return (None, "same_member")
    net1 = await _get_member_network_id(db, data.member_id_1)
    net2 = await _get_member_network_id(db, data.member_id_2)
    if not net1 or not net2:
        return (None, "not_found")
    if net1 != net2:
        return (None, "different_network")
    network_id = net1
    role = await get_user_role_in_network(db, network_id, user_id)
    if not _require_owner_or_admin(role):
        return (None, "forbidden")
    if await _has_active_marriage(db, data.member_id_1):
        return (None, "already_active")
    if await _has_active_marriage(db, data.member_id_2):
        return (None, "already_active")

    if data.create_new_family:
        family = Family(
            network_id=network_id,
            name="Gia đình mới",
            description=None,
            created_by=user_id,
            status=FamilyStatus.ACTIVE,
        )
        db.add(family)
        await db.flush()
        for mid in (data.member_id_1, data.member_id_2):
            member = await db.get(Member, mid)
            if member:
                member.family_id = family.id
        await db.flush()

    marriage = Marriage(
        member_id_1=data.member_id_1,
        member_id_2=data.member_id_2,
        marriage_date=data.marriage_date,
        status=MarriageStatus.ACTIVE,
    )
    db.add(marriage)
    await db.flush()
    await db.refresh(marriage)
    return (marriage, None)


async def list_marriages_for_family(
    db: AsyncSession,
    family_id: uuid.UUID,
    user_id: uuid.UUID,
) -> list[Marriage] | None:
    """List marriages where at least one member belongs to this family. User must be in network."""
    family = await db.get(Family, family_id)
    if not family:
        return None
    if await get_user_role_in_network(db, family.network_id, user_id) is None:
        return None
    subq = select(Member.id).where(Member.family_id == family_id)
    result = await db.execute(
        select(Marriage).where(
            or_(
                Marriage.member_id_1.in_(subq),
                Marriage.member_id_2.in_(subq),
            )
        ).order_by(Marriage.created_at.desc())
    )
    return list(result.scalars().unique().all())


async def list_marriages_for_network(
    db: AsyncSession,
    network_id: uuid.UUID,
    user_id: uuid.UUID,
) -> list[Marriage] | None:
    """List marriages where both members are in this network. User must be in network."""
    if await get_user_role_in_network(db, network_id, user_id) is None:
        return None
    # Marriages where member_1's family is in network (then member_2 must be in same network by creation rule)
    result = await db.execute(
        select(Marriage)
        .join(Member, Marriage.member_id_1 == Member.id)
        .join(Family, Member.family_id == Family.id)
        .where(Family.network_id == network_id)
        .order_by(Marriage.created_at.desc())
    )
    return list(result.scalars().unique().all())


async def get_marriage(
    db: AsyncSession,
    marriage_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Marriage | None:
    """Get marriage by id. User must be in the same network as the members."""
    marriage = await db.get(Marriage, marriage_id)
    if not marriage:
        return None
    network_id = await _get_member_network_id(db, marriage.member_id_1)
    if not network_id or await get_user_role_in_network(db, network_id, user_id) is None:
        return None
    return marriage


async def update_marriage(
    db: AsyncSession,
    marriage_id: uuid.UUID,
    user_id: uuid.UUID,
    data: MarriageUpdate,
) -> Marriage | None:
    """Update marriage status (e.g. DIVORCED, ENDED). Caller must be OWNER or ADMIN."""
    marriage = await db.get(Marriage, marriage_id)
    if not marriage:
        return None
    network_id = await _get_member_network_id(db, marriage.member_id_1)
    if not network_id:
        return None
    role = await get_user_role_in_network(db, network_id, user_id)
    if not _require_owner_or_admin(role):
        return None
    marriage.status = data.status
    await db.flush()
    await db.refresh(marriage)
    return marriage
