"""
Schemas for Marriage API.
"""
import uuid
from datetime import date
from pydantic import BaseModel

from app.models.relationship import MarriageStatus


class MarriageBase(BaseModel):
    person_a_id: uuid.UUID
    person_b_id: uuid.UUID
    start_date: date | None = None


class MarriageCreate(MarriageBase):
    pass


class MarriageEnd(BaseModel):
    end_date: date | None = None
    status: MarriageStatus = MarriageStatus.DIVORCED


class MarriageResponse(MarriageBase):
    id: uuid.UUID
    end_date: date | None = None
    status: MarriageStatus

    class Config:
        from_attributes = True
