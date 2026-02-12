"""
Schemas for Lineage API.
"""
import uuid
from datetime import datetime
from pydantic import BaseModel

from app.models.lineage import TraditionType


class LineageBase(BaseModel):
    name: str
    root_person_id: uuid.UUID | None = None
    tradition_type: TraditionType = TraditionType.PATRILINEAL


class LineageCreate(LineageBase):
    pass


class LineageResponse(LineageBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
