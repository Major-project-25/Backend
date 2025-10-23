# Backend/schema/post_schema.py

from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, Literal

# --- ADD THIS NEW SCHEMA ---
class ReactionCreate(BaseModel):
    # The reaction_type must be one of these three values
    reaction_type: Literal['like', 'dislike', 'none']

class PostResponse(BaseModel):
    id: UUID
    content: Optional[str]
    media_url: Optional[str]
    content_type: str
    created_at: datetime
    author_id: UUID
    
    # --- ADD THESE THREE LINES ---
    likes: int
    dislikes: int
    user_reaction: Optional[str] = None # 'like', 'dislike', or null

    class Config:
        from_attributes = True
