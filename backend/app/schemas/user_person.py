"""
Schemas for User-Person mapping API.
"""
import uuid
from pydantic import BaseModel


class UserPersonLink(BaseModel):
    person_id: uuid.UUID


class UserPersonActive(BaseModel):
    person_id: uuid.UUID


class PersonMappingResponse(BaseModel):
    person_id: uuid.UUID
    full_name: str

    class Config:
        from_attributes = True
