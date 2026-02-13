"""Add family_role to members

Revision ID: 007
Revises: 006
Create Date: 2025-02-13

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'memberfamilyrole') THEN
                CREATE TYPE memberfamilyrole AS ENUM ('HUSBAND', 'WIFE', 'CHILD', 'OTHER');
            END IF;
        END
        $$;
    """)
    memberfamilyrole_enum = postgresql.ENUM(
        "HUSBAND", "WIFE", "CHILD", "OTHER", name="memberfamilyrole", create_type=False
    )
    op.add_column(
        "members",
        sa.Column(
            "family_role",
            memberfamilyrole_enum,
            nullable=False,
            server_default="CHILD",
        ),
    )


def downgrade() -> None:
    op.drop_column("members", "family_role")
    op.execute("DROP TYPE memberfamilyrole")
