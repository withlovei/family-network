import enum
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class PostVisibility(str, enum.Enum):
    LINEAGE_PUBLIC = "LINEAGE_PUBLIC"
    DIRECT_FAMILY_PRIVATE = "DIRECT_FAMILY_PRIVATE"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    author_person_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persons.id", ondelete="CASCADE"),
        nullable=False,
    )
    visibility: Mapped[PostVisibility] = mapped_column(
        Enum(
            PostVisibility,
            name="post_visibility_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=PostVisibility.LINEAGE_PUBLIC,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

