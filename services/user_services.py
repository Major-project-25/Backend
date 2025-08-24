from sqlalchemy.orm import Session
from repositories import user_repo
from schema.user_schema import UserCreate

def register_user(db: Session, user: UserCreate):
    return user_repo.create_user(db, user)

def list_users(db: Session):
    return user_repo.get_users(db)
