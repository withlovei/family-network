"""
Core domain tables: person, lineage, parent_child, marriages, user_person, posts

Revision ID: 002
Revises: 001
Create Date: 2026-02-12
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # persons
    op.create_table(
        "persons",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column(
            "gender",
            sa.Enum("male", "female", name="gender_enum"),
            nullable=False,
        ),
        sa.Column("birth_date", sa.Date(), nullable=True),
        sa.Column("death_date", sa.Date(), nullable=True),
        sa.Column("primary_lineage_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )

    # lineages
    op.create_table(
        "lineages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("root_person_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "tradition_type",
            sa.Enum("patrilineal", "modern", name="tradition_type_enum"),
            nullable=False,
            server_default="patrilineal",
        ),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
    )

    # parent_child
    op.create_table(
        "parent_child",
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "relation_type",
            sa.Enum("biological", "adopted", name="relation_type_enum"),
            nullable=False,
            server_default="biological",
        ),
        sa.ForeignKeyConstraint(["parent_id"], ["persons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["child_id"], ["persons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("parent_id", "child_id"),
    )

    # marriages
    op.create_table(
        "marriages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("person_a_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("person_b_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("married", "divorced", "widowed", name="marriage_status_enum"),
            nullable=False,
            server_default="married",
        ),
        sa.ForeignKeyConstraint(["person_a_id"], ["persons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["person_b_id"], ["persons.id"], ondelete="CASCADE"),
    )
    op.create_index(
        "ix_marriages_person_a_b",
        "marriages",
        ["person_a_id", "person_b_id"],
        unique=False,
    )

    # user_person
    op.create_table(
        "user_person",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("person_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["person_id"], ["persons.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "person_id"),
    )

    # posts
    op.create_table(
        "posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("author_person_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "visibility",
            sa.Enum(
                "LINEAGE_PUBLIC",
                "DIRECT_FAMILY_PRIVATE",
                name="post_visibility_enum",
            ),
            nullable=False,
            server_default="LINEAGE_PUBLIC",
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["author_person_id"], ["persons.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_posts_author_person_id", "posts", ["author_person_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_posts_author_person_id", table_name="posts")
    op.drop_table("posts")
    op.drop_table("user_person")
    op.drop_index("ix_marriages_person_a_b", table_name="marriages")
    op.drop_table("marriages")
    op.drop_table("parent_child")
    op.drop_table("lineages")
    op.drop_table("persons")

    op.execute("DROP TYPE post_visibility_enum")
    op.execute("DROP TYPE marriage_status_enum")
    op.execute("DROP TYPE relation_type_enum")
    op.execute("DROP TYPE tradition_type_enum")
    op.execute("DROP TYPE gender_enum")

