"""Family networks and network_user_roles tables

Revision ID: 003
Revises: 002
Create Date: 2025-02-13

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types only if they don't exist (idempotent for re-runs after partial failure)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'networkstatus') THEN
                CREATE TYPE networkstatus AS ENUM ('ACTIVE', 'ARCHIVED');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'networkrole') THEN
                CREATE TYPE networkrole AS ENUM ('OWNER', 'ADMIN', 'MEMBER', 'VIEWER');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'networkuserrolestatus') THEN
                CREATE TYPE networkuserrolestatus AS ENUM ('ACTIVE', 'REMOVED');
            END IF;
        END
        $$;
    """)

    networkstatus_enum = postgresql.ENUM(
        "ACTIVE", "ARCHIVED", name="networkstatus", create_type=False
    )
    networkrole_enum = postgresql.ENUM(
        "OWNER", "ADMIN", "MEMBER", "VIEWER", name="networkrole", create_type=False
    )
    networkuserrolestatus_enum = postgresql.ENUM(
        "ACTIVE", "REMOVED", name="networkuserrolestatus", create_type=False
    )

    op.create_table(
        "family_networks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "status",
            networkstatus_enum,
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_family_networks_created_by"),
        "family_networks",
        ["created_by"],
        unique=False,
    )

    op.create_table(
        "network_user_roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("network_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "role",
            networkrole_enum,
            nullable=False,
        ),
        sa.Column(
            "status",
            networkuserrolestatus_enum,
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["network_id"], ["family_networks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("network_id", "user_id", name="uq_network_user_roles_network_user"),
    )
    op.create_index(
        op.f("ix_network_user_roles_network_id"),
        "network_user_roles",
        ["network_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_network_user_roles_user_id"),
        "network_user_roles",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_network_user_roles_user_id"), table_name="network_user_roles")
    op.drop_index(op.f("ix_network_user_roles_network_id"), table_name="network_user_roles")
    op.drop_table("network_user_roles")
    op.drop_index(op.f("ix_family_networks_created_by"), table_name="family_networks")
    op.drop_table("family_networks")
    op.execute("DROP TYPE networkuserrolestatus")
    op.execute("DROP TYPE networkrole")
    op.execute("DROP TYPE networkstatus")
