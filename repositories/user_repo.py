from sqlalchemy.orm import Session
from model.user import User
from schema.user_schema import UserCreate, AccountSetup
from core.security import hash_password
from uuid import UUID

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

# For the Login API and general use
def get_user_by_email(db: Session, email: str) -> User | None:
    """Fetches a single user by their email address."""
    return db.query(User).filter(User.email == email).first()