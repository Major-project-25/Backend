# Backend/schema/post_schema.py

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class PostResponse(BaseModel):
    id: UUID
    content: str | None
    media_url: str | None
    content_type: str
    created_at: datetime
    author_id: UUID

    class Config:
        from_attributes = True