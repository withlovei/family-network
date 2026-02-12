"""
Schemas for Post API.
"""
import uuid
from datetime import datetime
from pydantic import BaseModel

from app.models.post import PostVisibility


class PostBase(BaseModel):
    visibility: PostVisibility = PostVisibility.LINEAGE_PUBLIC
    content: str


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
