"""
Add index on persons.primary_lineage_id

Revision ID: 003
Revises: 002
Create Date: 2026-02-12
"""
from typing import Sequence, Union

from alembic import op


revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_persons_primary_lineage_id",
        "persons",
        ["primary_lineage_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_persons_primary_lineage_id", table_name="persons")

