import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class UserPerson(Base):
  __tablename__ = "user_person"

  user_id: Mapped[uuid.UUID] = mapped_column(
      UUID(as_uuid=True),
      ForeignKey("users.id", ondelete="CASCADE"),
      primary_key=True,
  )
  person_id: Mapped[uuid.UUID] = mapped_column(
      UUID(as_uuid=True),
      ForeignKey("persons.id", ondelete="CASCADE"),
      primary_key=True,
  )

