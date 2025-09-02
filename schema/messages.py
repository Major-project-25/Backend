# schema/messages.py

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import List

class MessageCreate(BaseModel):
    """ Schema for sending a new message via WebSocket. """
    receiver_id: UUID
    content: str

class MessageResponse(BaseModel):
    """ Schema for representing a single message in a response. """
    id: int
    sender_id: UUID
    receiver_id: UUID
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True

class MeetLinkResponse(BaseModel):
    """ Schema for the Google Meet link response. """
    meet_link: str

