from pydantic import BaseModel, EmailStr
from typing import List, Optional
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    name: str
    university_reg_no: str
    biography: Optional[str] = None
    interest1: Optional[str] = None
    interest2: Optional[str] = None
    interest3: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: UUID
    matched_profiles: List[UUID] = []

    class Config:
        orm_mode = True
