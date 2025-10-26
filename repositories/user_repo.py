from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from model.user import User
from schema.user_schema import UserCreate, AccountSetup
from core.security import hash_password
from uuid import UUID
from typing import List
from datetime import date

# For the Sign-Up API
def create_user(db: Session, user: UserCreate) -> User:
    """Creates a new user with only email and a hashed password."""
    hashed_pass = hash_password(user.password)
    db_user = User(email=user.email, password=hashed_pass)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def setup_user_account(db: Session, user_id: UUID, profile_data: AccountSetup) -> User | None:
    """Finds a user by ID and updates their profile with the new interest structure."""
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        return None

    # Get the data from the Pydantic model
    update_data = profile_data.model_dump(exclude_unset=True)
    
    # Update the user object's attributes
    for key, value in update_data.items():
        setattr(db_user, key, value)
        
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_daily_matches(db: Session, user_id: UUID, daily_matches: List[UUID], generation_date: date) -> User | None:
    """
    Finds a user by their ID and updates their daily_matches list and
    the matches_generated_at date.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        return None

    # Use the exact column names from your schema
    setattr(db_user, 'daily_matches', daily_matches)
    setattr(db_user, 'matches_generated_at', generation_date)
    
    db.commit()
    db.refresh(db_user)
    return db_user

# For the Login API and general use
def get_user_by_email(db: Session, email: str) -> User | None:
    """Fetches a single user by their email address."""
    return db.query(User).filter(User.email == email).first()

def get_all_active_users(db: Session) -> List[User]:
    """
    Fetches all users who have set at least one interest.
    These are the users who are eligible for matching.
    """
    return db.query(User).filter(User.name != None, User.interest1 != None).all()

def update_user_matches(db: Session, user_id: UUID, matched_ids: List[UUID]) -> User | None:
    """
    Finds a user by their ID and updates their matched_profiles list.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        return None

    setattr(db_user, 'matched_profiles', matched_ids)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_reg_no(db: Session, reg_no: str) -> User | None:
    """
    Fetches a single user by their university registration number.
    """
    return db.query(User).filter(User.university_reg_no == reg_no).first()

def get_user_by_id(db: Session, user_id: UUID) -> User | None:
    """ Fetches a single user by their primary key ID. """
    return db.query(User).filter(User.id == user_id).first()