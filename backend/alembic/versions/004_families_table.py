"""Families table

Revision ID: 004
Revises: 003
Create Date: 2025-02-13

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'familystatus') THEN
                CREATE TYPE familystatus AS ENUM ('ACTIVE', 'ARCHIVED', 'MERGED');
            END IF;
        END
        $$;
    """)
    familystatus_enum = postgresql.ENUM(
        "ACTIVE", "ARCHIVED", "MERGED", name="familystatus", create_type=False
    )
    op.create_table(
        "families",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("network_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "status",
            familystatus_enum,
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["network_id"], ["family_networks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_families_network_id"),
        "families",
        ["network_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_families_network_id"), table_name="families")
    op.drop_table("families")
    op.execute("DROP TYPE familystatus")
