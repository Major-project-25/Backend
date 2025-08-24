from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from DB.session import get_db
from schema.user_schema import UserCreate, UserRead, AccountSetup, ValidationResponse, BooleanResponse 
from services.user_services import register_user, list_users
from repositories import user_repo
from core.security import verify_password, create_access_token
from uuid import UUID

router = APIRouter()

# 1. MODIFIED "Sign-Up" API to act as a credential checker
@router.post("/signup", response_model=ValidationResponse)
def signup_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Handles new user sign-up.
    - If email is new, creates user and returns True + new UUID.
    - If email exists, returns False.
    """
    # 1. Check if a user with this email already exists
    existing_user = user_repo.get_user_by_email(db, email=user_data.email)

    if existing_user:
        # 2. If user exists, return False and no ID
        return {"is_valid": False, "user_id": None}
    
    # 3. If user does not exist, create a new one
    new_user = user_repo.create_user(db, user=user_data)
    
    # 4. Return True and the UUID of the newly created user
    return {"is_valid": True, "user_id": new_user.id}

# 3. Account Setup API
@router.put("/{user_id}/setup", response_model=BooleanResponse)
def setup_user_profile(user_id: UUID, profile_data: AccountSetup, db: Session = Depends(get_db)):
    """
    Updates a user's profile.
    Returns true if the update was successful, otherwise false.
    """
    updated_user = user_repo.setup_user_account(
        db=db, user_id=user_id, profile_data=profile_data
    )
    
    # If the user was found and updated, updated_user will not be None
    if updated_user:
        return {"is_valid": True}
    else:
        # If the user was not found, return false
        return {"is_valid": False}