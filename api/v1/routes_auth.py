# routes_auth.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from DB.session import get_db
from schema.user_schema import UserCreate, ValidationResponse
from services import user_services

router = APIRouter()

@router.post("/login", response_model=ValidationResponse)
def login_user(login_data: UserCreate, db: Session = Depends(get_db)):
    """
    Handles user login by calling the authentication service.
    - If credentials are correct, returns True + user's UUID.
    - If credentials are incorrect, returns False.
    """
    # Call the service to handle all authentication logic
    authenticated_user = user_services.authenticate_user_service(db, login_data=login_data)

    if authenticated_user:
        # If the service returns a user object, login was successful
        return {"is_valid": True, "user_id": authenticated_user.id}
    else:
        # If the service returns None, credentials were invalid
        return {"is_valid": False, "user_id": None}