# routes_users.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from DB.session import get_db
from schema.user_schema import UserCreate, AccountSetup, ValidationResponse, BooleanResponse, UserProfile
from services import user_services
from repositories import user_repo

router = APIRouter()

@router.post("/signup", response_model=ValidationResponse)
def signup_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Handles new user sign-up by calling the registration service.
    - If email is new, creates user and returns True + new UUID.
    - If email exists, returns False.
    """
    # Call the service to handle all registration logic
    new_user = user_services.register_user_service(db, user_data=user_data)
    
    if new_user:
        # If the service returns a user object, registration was successful
        return {"is_valid": True, "user_id": new_user.id}
    else:
        # If the service returns None, the user already existed
        return {"is_valid": False, "user_id": None}

@router.put("/{user_id}/setup", response_model=BooleanResponse)
def setup_user_profile(user_id: UUID, profile_data: AccountSetup, db: Session = Depends(get_db)):
    """
    Updates a user's profile by calling the setup service.
    Returns true if the update was successful, otherwise false.
    """
    # Call the service to handle the profile setup logic
    updated_user = user_services.setup_profile_service(
        db=db, user_id=user_id, profile_data=profile_data
    )
    
    # If the user was found and updated, the service returns the user object
    if updated_user:
        return {"is_valid": True}
    else:
        # If the user was not found, the service returns None
        return {"is_valid": False}
    

@router.get("/{user_id}/profile", response_model=UserProfile)
def get_user_profile(user_id: UUID, db: Session = Depends(get_db)):
    """
    Fetches a user's public profile details (USN, bio, and interests)
    using their UUID.
    """
    # The get_user_by_id function already exists in your repo
    user = user_repo.get_user_by_id(db, user_id=user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this ID not found.",
        )
    
    return user