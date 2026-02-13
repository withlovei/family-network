import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from app.models.family_network import NetworkStatus, NetworkRole


class NetworkBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class NetworkCreate(NetworkBase):
    pass


class NetworkUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: NetworkStatus | None = None


class NetworkResponse(NetworkBase):
    id: uuid.UUID
    created_by: uuid.UUID | None
    status: NetworkStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NetworkWithRoleResponse(NetworkResponse):
    """Network list item including current user's role in that network."""

    my_role: str


class NetworkMemberAdd(BaseModel):
    email: EmailStr
    role: NetworkRole = NetworkRole.MEMBER


class NetworkMemberUpdate(BaseModel):
    role: NetworkRole


class NetworkMemberResponse(BaseModel):
    user_id: uuid.UUID
    email: str
    full_name: str
    role: str
    status: str

    class Config:
        from_attributes = True
