from pydantic import BaseModel, EmailStr
from typing import List, Optional
from uuid import UUID

# --- User Schemas ---

class BooleanResponse(BaseModel):
    is_valid: bool

class ValidationResponse(BaseModel):
    is_valid: bool
    user_id: Optional[UUID] = None

# Schema for the Sign-Up API (only email and password)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Schema for the Account Setup API
class AccountSetup(BaseModel):
    name: str
    university_reg_no: str
    biography: Optional[str] = None
    interest1: Optional[str] = None
    interest1_weight: Optional[int] = None
    interest2: Optional[str] = None
    interest2_weight: Optional[int] = None
    interest3: Optional[str] = None
    interest3_weight: Optional[int] = None

# Schema for returning user data
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

# Defines the expected JSON body for the login request
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# A simple schema for returning a status message
class StatusResponse(BaseModel):
    message: str
