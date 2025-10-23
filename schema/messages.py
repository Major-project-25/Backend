# schema/messages.py

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List, Optional

class MessageCreate(BaseModel):
    """ Schema for sending a new message via WebSocket. """
    receiver_id: UUID
    # MODIFIED: Both content and media_url are now optional
    content: Optional[str] = None
    media_url: Optional[str] = None
    message_type: str = 'text'

class MessageResponse(BaseModel):
    """ Schema for representing a single message in a response. """
    id: int
    sender_id: UUID
    receiver_id: UUID
    # MODIFIED: Both content and media_url are now optional
    content: Optional[str] = None
    media_url: Optional[str] = None
    message_type: str
    timestamp: datetime

    class Config:
        from_attributes = True

class MeetLinkResponse(BaseModel):
    """ Schema for the Google Meet link response. """
    meet_link: str

# --- ADD THIS NEW SCHEMA ---
class MediaUploadResponse(BaseModel):
    """ Schema for the response after a successful media upload. """
    media_url: str
