import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.family_network import (
    FamilyNetwork,
    NetworkUserRole,
    NetworkStatus,
    NetworkRole,
    NetworkUserRoleStatus,
)
from app.models.user import User
from app.schemas.network import NetworkCreate, NetworkUpdate, NetworkMemberAdd, NetworkMemberUpdate


async def create_network(
    db: AsyncSession,
    user_id: uuid.UUID,
    data: NetworkCreate,
) -> FamilyNetwork:
    """Create a family network and add creator as OWNER."""
    network = FamilyNetwork(
        name=data.name,
        description=data.description,
        created_by=user_id,
        status=NetworkStatus.ACTIVE,
    )
    db.add(network)
    await db.flush()
    role = NetworkUserRole(
        network_id=network.id,
        user_id=user_id,
        role=NetworkRole.OWNER,
        status=NetworkUserRoleStatus.ACTIVE,
    )
    db.add(role)
    await db.flush()
    await db.refresh(network)
    return network


async def get_user_role_in_network(
    db: AsyncSession,
    network_id: uuid.UUID,
    user_id: uuid.UUID,
) -> NetworkUserRole | None:
    """Return the user's active role in the network, or None."""
    result = await db.execute(
        select(NetworkUserRole).where(
            NetworkUserRole.network_id == network_id,
            NetworkUserRole.user_id == user_id,
            NetworkUserRole.status == NetworkUserRoleStatus.ACTIVE,
        )
    )
    return result.scalar_one_or_none()


async def list_networks_for_user(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> list[tuple[FamilyNetwork, str]]:
    """List networks the user is a member of (active role). Returns (network, my_role)."""
    result = await db.execute(
        select(FamilyNetwork, NetworkUserRole.role).join(
            NetworkUserRole,
            (NetworkUserRole.network_id == FamilyNetwork.id)
            & (NetworkUserRole.user_id == user_id)
            & (NetworkUserRole.status == NetworkUserRoleStatus.ACTIVE),
        ).order_by(FamilyNetwork.created_at.desc())
    )
    return [(row[0], row[1].value) for row in result.all()]


async def get_network(
    db: AsyncSession,
    network_id: uuid.UUID,
    user_id: uuid.UUID,
) -> tuple[FamilyNetwork, str] | None:
    """Get network by id if user has access. Returns (network, my_role) or None."""
    role = await get_user_role_in_network(db, network_id, user_id)
    if not role:
        return None
    network = await db.get(FamilyNetwork, network_id)
    if not network:
        return None
    return (network, role.role.value)


async def update_network(
    db: AsyncSession,
    network_id: uuid.UUID,
    user_id: uuid.UUID,
    data: NetworkUpdate,
) -> FamilyNetwork | None:
    """Update network. Only OWNER or ADMIN. Returns updated network or None if not found/forbidden."""
    role = await get_user_role_in_network(db, network_id, user_id)
    if not role or role.role not in (NetworkRole.OWNER, NetworkRole.ADMIN):
        return None
    network = await db.get(FamilyNetwork, network_id)
    if not network:
        return None
    if data.name is not None:
        network.name = data.name
    if data.description is not None:
        network.description = data.description
    if data.status is not None:
        network.status = data.status
    await db.flush()
    await db.refresh(network)
    return network


async def archive_network(
    db: AsyncSession,
    network_id: uuid.UUID,
    user_id: uuid.UUID,
) -> FamilyNetwork | None:
    """Set network status to ARCHIVED. Only OWNER. Returns network or None."""
    role = await get_user_role_in_network(db, network_id, user_id)
    if not role or role.role != NetworkRole.OWNER:
        return None
    network = await db.get(FamilyNetwork, network_id)
    if not network:
        return None
    network.status = NetworkStatus.ARCHIVED
    await db.flush()
    await db.refresh(network)
    return network


def _require_owner_or_admin(role: NetworkUserRole | None) -> bool:
    return role is not None and role.role in (NetworkRole.OWNER, NetworkRole.ADMIN)


async def list_network_members(
    db: AsyncSession,
    network_id: uuid.UUID,
    caller_id: uuid.UUID,
) -> list[dict] | None:
    """List all members (active roles) of the network. Caller must be a member. Returns None if no access."""
    if await get_user_role_in_network(db, network_id, caller_id) is None:
        return None
    result = await db.execute(
        select(NetworkUserRole, User.email, User.full_name).join(
            User,
            User.id == NetworkUserRole.user_id,
        ).where(
            NetworkUserRole.network_id == network_id,
            NetworkUserRole.status == NetworkUserRoleStatus.ACTIVE,
        ).order_by(NetworkUserRole.role.asc(), User.email.asc())
    )
    rows = result.all()
    return [
        {
            "user_id": r[0].user_id,
            "email": r[1],
            "full_name": r[2],
            "role": r[0].role.value,
            "status": r[0].status.value,
        }
        for r in rows
    ]


async def add_member_by_email(
    db: AsyncSession,
    network_id: uuid.UUID,
    caller_id: uuid.UUID,
    data: NetworkMemberAdd,
) -> tuple[dict | None, str | None]:
    """Add user to network by email. Caller must be OWNER or ADMIN.
    Returns (member_dict, None) on success, (None, 'user_not_found' | 'already_in_network') on error, (None, None) if forbidden."""
    from app.services.auth import get_user_by_email

    caller_role = await get_user_role_in_network(db, network_id, caller_id)
    if not _require_owner_or_admin(caller_role):
        return (None, None)
    network = await db.get(FamilyNetwork, network_id)
    if not network:
        return (None, None)
    user = await get_user_by_email(db, data.email)
    if not user:
        return (None, "user_not_found")
    existing = await get_user_role_in_network(db, network_id, user.id)
    if existing:
        return (None, "already_in_network")
    role = NetworkUserRole(
        network_id=network_id,
        user_id=user.id,
        role=data.role,
        status=NetworkUserRoleStatus.ACTIVE,
    )
    db.add(role)
    await db.flush()
    return (
        {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": role.role.value,
            "status": role.status.value,
        },
        None,
    )


async def update_member_role(
    db: AsyncSession,
    network_id: uuid.UUID,
    target_user_id: uuid.UUID,
    caller_id: uuid.UUID,
    data: NetworkMemberUpdate,
) -> tuple[dict | None, str | None]:
    """Update a member's role. Returns (member_dict, None) or (None, 'forbidden' | 'not_found' | 'cannot_change_owner')."""
    caller_role = await get_user_role_in_network(db, network_id, caller_id)
    if not _require_owner_or_admin(caller_role):
        return (None, "forbidden")
    target_role_row = await get_user_role_in_network(db, network_id, target_user_id)
    if not target_role_row:
        return (None, "not_found")
    if target_role_row.role == NetworkRole.OWNER:
        return (None, "cannot_change_owner")
    target_role_row.role = data.role
    await db.flush()
    user = await db.get(User, target_user_id)
    if not user:
        return (None, "not_found")
    return (
        {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": target_role_row.role.value,
            "status": target_role_row.status.value,
        },
        None,
    )


async def remove_member(
    db: AsyncSession,
    network_id: uuid.UUID,
    target_user_id: uuid.UUID,
    caller_id: uuid.UUID,
) -> tuple[bool, str | None]:
    """Set member's status to REMOVED. Returns (True, None) or (False, 'forbidden' | 'not_found' | 'cannot_remove_owner')."""
    caller_role = await get_user_role_in_network(db, network_id, caller_id)
    if not _require_owner_or_admin(caller_role):
        return (False, "forbidden")
    result = await db.execute(
        select(NetworkUserRole).where(
            NetworkUserRole.network_id == network_id,
            NetworkUserRole.user_id == target_user_id,
            NetworkUserRole.status == NetworkUserRoleStatus.ACTIVE,
        )
    )
    target = result.scalar_one_or_none()
    if not target:
        return (False, "not_found")
    if target.role == NetworkRole.OWNER:
        return (False, "cannot_remove_owner")
    target.status = NetworkUserRoleStatus.REMOVED
    await db.flush()
    return (True, None)
