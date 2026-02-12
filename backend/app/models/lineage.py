import enum
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class TraditionType(str, enum.Enum):
    PATRILINEAL = "patrilineal"
    MODERN = "modern"


class Lineage(Base):
    __tablename__ = "lineages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    root_person_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    tradition_type: Mapped[TraditionType] = mapped_column(
        Enum(
            TraditionType,
            name="tradition_type_enum",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        default=TraditionType.PATRILINEAL,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

