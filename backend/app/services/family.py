import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.family_network import (
    FamilyNetwork,
    Family,
    FamilyStatus,
    NetworkUserRole,
    NetworkRole,
    NetworkUserRoleStatus,
)
from app.schemas.family import FamilyCreate, FamilyUpdate
from app.services.network import get_user_role_in_network


def _require_owner_or_admin(role: NetworkUserRole | None) -> bool:
    return role is not None and role.role in (NetworkRole.OWNER, NetworkRole.ADMIN)


async def create_family(
    db: AsyncSession,
    network_id: uuid.UUID,
    user_id: uuid.UUID,
    data: FamilyCreate,
) -> Family | None:
    """Create a family in the network. Caller must be OWNER or ADMIN."""
    role = await get_user_role_in_network(db, network_id, user_id)
    if not _require_owner_or_admin(role):
        return None
    network = await db.get(FamilyNetwork, network_id)
    if not network:
        return None
    family = Family(
        network_id=network_id,
        name=data.name,
        description=data.description,
        created_by=user_id,
        status=FamilyStatus.ACTIVE,
    )
    db.add(family)
    await db.flush()
    await db.refresh(family)
    return family


async def list_families_for_network(
    db: AsyncSession,
    network_id: uuid.UUID,
    user_id: uuid.UUID,
) -> list[Family] | None:
    """List families in the network. User must be a member (any role)."""
    if await get_user_role_in_network(db, network_id, user_id) is None:
        return None
    result = await db.execute(
        select(Family).where(Family.network_id == network_id).order_by(Family.created_at.desc())
    )
    return list(result.scalars().all())


async def get_family(
    db: AsyncSession,
    family_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Family | None:
    """Get family by id. User must be a member of the family's network."""
    family = await db.get(Family, family_id)
    if not family:
        return None
    if await get_user_role_in_network(db, family.network_id, user_id) is None:
        return None
    return family


async def update_family(
    db: AsyncSession,
    family_id: uuid.UUID,
    user_id: uuid.UUID,
    data: FamilyUpdate,
) -> Family | None:
    """Update family. Caller must be OWNER or ADMIN of the network."""
    family = await db.get(Family, family_id)
    if not family:
        return None
    role = await get_user_role_in_network(db, family.network_id, user_id)
    if not _require_owner_or_admin(role):
        return None
    if data.name is not None:
        family.name = data.name
    if data.description is not None:
        family.description = data.description
    if data.status is not None:
        family.status = data.status
    await db.flush()
    await db.refresh(family)
    return family


async def archive_family(
    db: AsyncSession,
    family_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Family | None:
    """Set family status to ARCHIVED. Caller must be OWNER or ADMIN."""
    family = await db.get(Family, family_id)
    if not family:
        return None
    role = await get_user_role_in_network(db, family.network_id, user_id)
    if not _require_owner_or_admin(role):
        return None
    family.status = FamilyStatus.ARCHIVED
    await db.flush()
    await db.refresh(family)
    return family
