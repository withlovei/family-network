import uuid
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.family_network import FamilyStatus


class FamilyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    address: str | None = None


class FamilyCreate(FamilyBase):
    pass


class FamilyUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    address: str | None = None
    status: FamilyStatus | None = None


class FamilyResponse(FamilyBase):
    id: uuid.UUID
    network_id: uuid.UUID
    created_by: uuid.UUID | None
    status: FamilyStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
