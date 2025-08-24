from sqlalchemy.orm import Session
from model.user import User
from schema.user_schema import UserCreate
from core.security import hash_password

def create_user(db: Session, user: UserCreate):
    db_user = User(
        email=user.email,
        name=user.name,
        university_reg_no=user.university_reg_no,
        password=hash_password(user.password),
        biography=user.biography,
        interest1=user.interest1,
        interest2=user.interest2,
        interest3=user.interest3,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()
