"""
Schemas for Person API.
"""
import uuid
from datetime import date, datetime
from pydantic import BaseModel

from app.models.person import Gender


class PersonBase(BaseModel):
    full_name: str
    gender: Gender
    birth_date: date | None = None
    death_date: date | None = None
    primary_lineage_id: uuid.UUID | None = None


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    full_name: str | None = None
    gender: Gender | None = None
    birth_date: date | None = None
    death_date: date | None = None
    primary_lineage_id: uuid.UUID | None = None


class PersonResponse(PersonBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
