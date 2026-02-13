import uuid
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.models.member import MemberGender, MemberStatus


class MemberBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    gender: MemberGender
    date_of_birth: date | None = None
    is_alive: bool = True


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=255)
    gender: MemberGender | None = None
    date_of_birth: date | None = None
    is_alive: bool | None = None


class MemberResponse(MemberBase):
    id: uuid.UUID
    family_id: uuid.UUID
    linked_user_id: uuid.UUID | None
    status: MemberStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MemberLinkUser(BaseModel):
    user_id: uuid.UUID
