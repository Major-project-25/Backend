# user_schema.py

from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID

# --- Response Schemas ---

class BooleanResponse(BaseModel):
    is_valid: bool

class ValidationResponse(BaseModel):
    is_valid: bool
    user_id: Optional[UUID] = None

class StatusResponse(BaseModel):
    message: str

# --- Data Schemas ---

# Schema for Sign-Up AND Login (requires email and password)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Schema for the Account Setup API
class AccountSetup(BaseModel):
    name: Optional[str] = None
    university_reg_no: Optional[str] = None
    biography: Optional[str] = None
    interest1: Optional[str] = None
    interest1_weight: Optional[int] = None
    interest2: Optional[str] = None
    interest2_weight: Optional[int] = None
    interest3: Optional[str] = None
    interest3_weight: Optional[int] = None

"""# Schema for returning user data to the client
class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    name: Optional[str] = None
    university_reg_no: Optional[str] = None
    biography: Optional[str] = None
    interest1: Optional[str] = None
    interest1_weight: Optional[int] = None
    interest2: Optional[str] = None
    interest2_weight: Optional[int] = None
    interest3: Optional[str] = None
    interest3_weight: Optional[int] = None

    class Config:
        from_attributes = True
"""

class UserProfile(BaseModel):
    """
    Defines the public profile information for a user.
    """
    university_reg_no: Optional[str] = None
    biography: Optional[str] = None
    interest1: Optional[str] = None
    interest2: Optional[str] = None
    interest3: Optional[str] = None

    class Config:
        from_attributes = True