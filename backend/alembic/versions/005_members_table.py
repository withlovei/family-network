"""Members table

Revision ID: 005
Revises: 004
Create Date: 2025-02-13

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'membergender') THEN
                CREATE TYPE membergender AS ENUM ('MALE', 'FEMALE', 'OTHER');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'memberstatus') THEN
                CREATE TYPE memberstatus AS ENUM ('ACTIVE', 'REMOVED');
            END IF;
        END
        $$;
    """)
    membergender_enum = postgresql.ENUM(
        "MALE", "FEMALE", "OTHER", name="membergender", create_type=False
    )
    memberstatus_enum = postgresql.ENUM(
        "ACTIVE", "REMOVED", name="memberstatus", create_type=False
    )
    op.create_table(
        "members",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("family_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column(
            "gender",
            membergender_enum,
            nullable=False,
        ),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("is_alive", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("linked_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "status",
            memberstatus_enum,
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["family_id"], ["families.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["linked_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_members_family_id"),
        "members",
        ["family_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_members_linked_user_id"),
        "members",
        ["linked_user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_members_linked_user_id"), table_name="members")
    op.drop_index(op.f("ix_members_family_id"), table_name="members")
    op.drop_table("members")
    op.execute("DROP TYPE memberstatus")
    op.execute("DROP TYPE membergender")
