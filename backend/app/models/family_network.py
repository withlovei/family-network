import enum
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Enum, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class NetworkStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class FamilyNetwork(Base):
    __tablename__ = "family_networks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[NetworkStatus] = mapped_column(
        Enum(NetworkStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=NetworkStatus.ACTIVE,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    user_roles: Mapped[list["NetworkUserRole"]] = relationship(
        "NetworkUserRole",
        back_populates="network",
        lazy="selectin",
    )
    families: Mapped[list["Family"]] = relationship(
        "Family",
        back_populates="network",
        lazy="selectin",
    )


class FamilyStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    MERGED = "MERGED"


class Family(Base):
    __tablename__ = "families"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    network_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("family_networks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[FamilyStatus] = mapped_column(
        Enum(FamilyStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=FamilyStatus.ACTIVE,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    network: Mapped["FamilyNetwork"] = relationship(
        "FamilyNetwork",
        back_populates="families",
    )
    members: Mapped[list["Member"]] = relationship(
        "Member",
        back_populates="family",
        lazy="selectin",
    )


class NetworkRole(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"


class NetworkUserRoleStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    REMOVED = "REMOVED"


class NetworkUserRole(Base):
    __tablename__ = "network_user_roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    network_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("family_networks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[NetworkRole] = mapped_column(
        Enum(NetworkRole, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    status: Mapped[NetworkUserRoleStatus] = mapped_column(
        Enum(NetworkUserRoleStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=NetworkUserRoleStatus.ACTIVE,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    network: Mapped["FamilyNetwork"] = relationship(
        "FamilyNetwork",
        back_populates="user_roles",
    )

    __table_args__ = (UniqueConstraint("network_id", "user_id", name="uq_network_user_roles_network_user"),)
