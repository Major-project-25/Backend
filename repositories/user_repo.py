from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, select # Added select
from model.user import User
from model.connections import Connection # Added Connection
from schema.user_schema import UserCreate, AccountSetup
from core.security import hash_password
from uuid import UUID
from typing import List
from datetime import date

# For the Sign-Up API
def create_user(db: Session, user: UserCreate) -> User:
    """(Unchanged)"""
    hashed_pass = hash_password(user.password)
    db_user = User(email=user.email, password=hashed_pass)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def setup_user_account(db: Session, user_id: UUID, profile_data: AccountSetup) -> User | None:
    """(Unchanged)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        return None

    update_data = profile_data.model_dump(exclude_unset=True)
    
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

    # --- *** THIS IS THE FIX *** ---
    # Use direct assignment instead of setattr
    db_user.daily_matches = daily_matches
    db_user.matches_generated_at = generation_date
    # --- *** END OF FIX *** ---
    
    db.commit()
    db.refresh(db_user)
    return db_user

# (Rest of the functions are unchanged...)

def get_user_by_email(db: Session, email: str) -> User | None:
    """(Unchanged)"""
    return db.query(User).filter(User.email == email).first()

def get_all_active_users(db: Session) -> List[User]:
    """(Unchanged)"""
    return db.query(User).filter(User.name != None, User.interest1 != None).all()

def update_user_matches(db: Session, user_id: UUID, matched_ids: List[UUID]) -> User | None:
    """(Unchanged)"""
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        return None

    # Keeping setattr here as it was original, assuming it worked elsewhere
    setattr(db_user, 'matched_profiles', matched_ids) 
    
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_reg_no(db: Session, reg_no: str) -> User | None:
    """(Unchanged)"""
    return db.query(User).filter(User.university_reg_no == reg_no).first()

def get_user_by_id(db: Session, user_id: UUID) -> User | None:
    """(Unchanged)"""
    return db.query(User).filter(User.id == user_id).first()

def get_potential_matches(db: Session, user_id: UUID) -> List[User]:
    """(Unchanged - contains the select() fix for SAWarning)"""
    
    sent_connection_ids = select(Connection.addressee_id).where(
        and_(
            Connection.requester_id == user_id,
            or_(Connection.status == 'accepted', Connection.status == 'pending')
        )
    ).subquery()

    received_connection_ids = select(Connection.requester_id).where(
        and_(
            Connection.addressee_id == user_id,
            or_(Connection.status == 'accepted', Connection.status == 'pending')
        )
    ).subquery()

    potential_matches = db.query(User).filter(
        User.name != None, User.interest1 != None, 
        User.id != user_id,  
        User.id.notin_(sent_connection_ids),  
        User.id.notin_(received_connection_ids) 
    ).all()

    return potential_matches

