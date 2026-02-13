import uuid
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.models.marriage import MarriageStatus
from app.schemas.member import MemberCreate


class NewFamilyWithMarriageCreate(BaseModel):
    """Create a new family with one existing member (child) + new spouse; record marriage."""

    member_id: uuid.UUID  # existing member in the current family (the "child" getting married)
    spouse: MemberCreate  # the new person to add as spouse
    marriage_date: date | None = None


class MarriageCreate(BaseModel):
    member_id_1: uuid.UUID
    member_id_2: uuid.UUID
    marriage_date: date | None = None
    create_new_family: bool = False


class MarriageUpdate(BaseModel):
    status: MarriageStatus


class MarriageResponse(BaseModel):
    id: uuid.UUID
    member_id_1: uuid.UUID
    member_id_2: uuid.UUID
    marriage_date: date | None
    status: MarriageStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NewFamilyWithMarriageResponse(BaseModel):
    """Response after creating new family with marriage."""

    family_id: uuid.UUID
    marriage_id: uuid.UUID
