# schema/connection.py

from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

# --- Request Schemas ---

class ConnectionRequest(BaseModel):
    addressee_id: UUID

class ConnectionUpdate(BaseModel):
    requester_id: UUID
    new_status: str # Should be 'accepted' or 'declined'

# --- Response Schemas (CHANGED) ---

class StatusResponse(BaseModel):
    """ A simple message response. """
    message: str

class PendingRequestDetail(BaseModel):
    """ Details of a user who sent a pending request. """
    requester_id: UUID
    university_reg_no: Optional[str] = None
    biography: Optional[str] = None
    interest1: Optional[str] = None
    interest2: Optional[str] = None
    interest3: Optional[str] = None

    class Config:
        from_attributes = True

# --- THIS SECTION IS NEW AND CORRECTED ---

class FriendDetail(BaseModel):
    """ Defines the detailed information for a single friend. """
    user_id: UUID
    university_reg_no: Optional[str] = None
    name: Optional[str] = None

    class Config:
        from_attributes = True

class FriendsResponse(BaseModel):
    """ A list of detailed friend objects. """
    friends: List[FriendDetail]


# --- UNUSED (can be kept or removed) ---

class ConnectionUser(BaseModel):
    id: UUID
    name: str | None
    email: str

    class Config:
        from_attributes = True

class ConnectionStatus(BaseModel):
    requester: ConnectionUser
    addressee: ConnectionUser
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
