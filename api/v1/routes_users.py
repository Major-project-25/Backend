from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from DB.session import get_db
from schema.user_schema import UserCreate, UserRead
from services.user_services import register_user, list_users

router = APIRouter()

@router.post("/", response_model=UserRead)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user)

@router.get("/", response_model=List[UserRead])
def get_users(db: Session = Depends(get_db)):
    return list_users(db)
