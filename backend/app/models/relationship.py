import enum
import uuid
from datetime import date
from sqlalchemy import Date, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class RelationType(str, enum.Enum):
    BIOLOGICAL = "biological"
    ADOPTED = "adopted"


class MarriageStatus(str, enum.Enum):
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


class ParentChild(Base):
    __tablename__ = "parent_child"

    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persons.id", ondelete="CASCADE"),
        primary_key=True,
    )
    child_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persons.id", ondelete="CASCADE"),
        primary_key=True,
    )
    relation_type: Mapped[RelationType] = mapped_column(
        Enum(
            RelationType,
            name="relation_type_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=RelationType.BIOLOGICAL,
    )


class Marriage(Base):
    __tablename__ = "marriages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    person_a_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persons.id", ondelete="CASCADE"),
        nullable=False,
    )
    person_b_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persons.id", ondelete="CASCADE"),
        nullable=False,
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[MarriageStatus] = mapped_column(
        Enum(
            MarriageStatus,
            name="marriage_status_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=MarriageStatus.MARRIED,
        nullable=False,
    )

