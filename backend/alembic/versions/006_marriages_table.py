"""Marriages table

Revision ID: 006
Revises: 005
Create Date: 2025-02-13

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'marriagestatus') THEN
                CREATE TYPE marriagestatus AS ENUM ('ACTIVE', 'DIVORCED', 'ENDED');
            END IF;
        END
        $$;
    """)
    marriagestatus_enum = postgresql.ENUM(
        "ACTIVE", "DIVORCED", "ENDED", name="marriagestatus", create_type=False
    )
    op.create_table(
        "marriages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("member_id_1", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("member_id_2", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("marriage_date", sa.Date(), nullable=True),
        sa.Column(
            "status",
            marriagestatus_enum,
            nullable=False,
            server_default="ACTIVE",
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["member_id_1"], ["members.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["member_id_2"], ["members.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("member_id_1 != member_id_2", name="ck_marriage_different_members"),
    )
    op.create_index(
        op.f("ix_marriages_member_id_1"),
        "marriages",
        ["member_id_1"],
        unique=False,
    )
    op.create_index(
        op.f("ix_marriages_member_id_2"),
        "marriages",
        ["member_id_2"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_marriages_member_id_2"), table_name="marriages")
    op.drop_index(op.f("ix_marriages_member_id_1"), table_name="marriages")
    op.drop_table("marriages")
    op.execute("DROP TYPE marriagestatus")
