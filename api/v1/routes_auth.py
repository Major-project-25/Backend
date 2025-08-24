from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from DB.session import get_db
from schema.user_schema import UserCreate, ValidationResponse
from repositories import user_repo
from core.security import verify_password

router = APIRouter()

# Change the response_model to BooleanResponse
@router.post("/login", response_model=ValidationResponse)
def login_user(login_data: UserCreate, db: Session = Depends(get_db)):
    """
    Handles user login.
    - If credentials are correct, returns True + user's UUID.
    - If credentials are incorrect, returns False.
    """
    # 1. Find the user by email
    user = user_repo.get_user_by_email(db, email=login_data.email)

    # 2. Check if user exists and if the password matches
    if user and verify_password(login_data.password, user.password):
        # 3. If credentials are valid, return True and the user's ID
        return {"is_valid": True, "user_id": user.id}
    else:
        # 4. If credentials are not valid, return False
        return {"is_valid": False, "user_id": None}