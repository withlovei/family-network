"""Users: add status (ACTIVE, INACTIVE, LOCKED)

Revision ID: 002
Revises: 001
Create Date: 2025-02-13

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TYPE userstatus AS ENUM ('ACTIVE', 'INACTIVE', 'LOCKED')")
    op.add_column(
        "users",
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "INACTIVE", "LOCKED", name="userstatus"),
            nullable=False,
            server_default="ACTIVE",
        ),
    )
    op.execute("UPDATE users SET status = 'INACTIVE' WHERE is_active = false")


def downgrade() -> None:
    op.drop_column("users", "status")
    op.execute("DROP TYPE userstatus")
