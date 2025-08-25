# user_services.py

from sqlalchemy.orm import Session
from uuid import UUID
from repositories import user_repo
from schema.user_schema import UserCreate, AccountSetup
from typing import List, Dict
from model.user import User
from core.security import verify_password
from services.gale_shaples import recommend_gale_cosine
from services.fisher_yates import fisher_yates_names

def register_user_service(db: Session, user_data: UserCreate) -> User | None:
    """
    Business logic for registering a new user.
    - Checks if a user with the given email already exists.
    - If not, it creates the user.
    - Returns the new user object or None if the user already exists.
    """
    # 1. Check for an existing user
    existing_user = user_repo.get_user_by_email(db, email=user_data.email)
    
    # 2. If user exists, return None to indicate failure
    if existing_user:
        return None
    
    # 3. If user does not exist, create a new one via the repository
    new_user = user_repo.create_user(db, user=user_data)
    return new_user

def authenticate_user_service(db: Session, login_data: UserCreate) -> User | None:
    """
    Business logic for user authentication.
    - Finds the user by email.
    - Verifies the password.
    - Returns the user object if authentication is successful, otherwise None.
    """
    # 1. Find the user by email via the repository
    user = user_repo.get_user_by_email(db, email=login_data.email)

    # 2. Check if user exists and if the password matches
    if user and verify_password(login_data.password, user.password):
        # 3. If credentials are valid, return the user object
        return user
    
    # 4. If credentials are not valid, return None
    return None

def setup_profile_service(db: Session, user_id: UUID, profile_data: AccountSetup) -> User | None:
    """
    Business logic for updating a user's profile.
    - Checks if the new university registration number is already taken by another user.
    - If not, it calls the repository to perform the update.
    - Returns the updated user or raises an error.
    """
    # 1. Check if the registration number is already in use by another user
    existing_user = user_repo.get_user_by_reg_no(db, reg_no=profile_data.university_reg_no)
    
    # 2. If it exists AND it belongs to a different user, raise an error
    if existing_user and existing_user.id != user_id:
        raise ValueError(f"University registration number '{profile_data.university_reg_no}' is already in use.")

    # 3. If the check passes, proceed with updating the user account
    updated_user = user_repo.setup_user_account(
        db=db, user_id=user_id, profile_data=profile_data
    )
    return updated_user

def generate_and_store_matches(db: Session, user_id: UUID) -> List[UUID] | None:
    """
    Orchestrates the entire matching process for a given user.
    """
    # 1. Fetch all users from the database who have completed their profiles
    all_users = user_repo.get_all_active_users(db)
    
    if len(all_users) < 2:
        # Not enough users to create matches
        return []

    # 2. Format the data for the recommendation algorithm
    profiles: Dict[str, Dict[str, float]] = {}
    subjects = set()
    user_name_to_id: Dict[str, UUID] = {}
    user_id_to_name: Dict[UUID, str] = {}
    
    current_user_name = ""

    for user in all_users:
        user_name_to_id[user.name] = user.id
        user_id_to_name[user.id] = user.name
        if user.id == user_id:
            current_user_name = user.name

        interests = {}
        # Collect up to 3 interests and their weights from the user model
        if user.interest1 and user.interest1_weight is not None:
            interests[user.interest1] = float(user.interest1_weight)
            subjects.add(user.interest1)
        if user.interest2 and user.interest2_weight is not None:
            interests[user.interest2] = float(user.interest2_weight)
            subjects.add(user.interest2)
        if user.interest3 and user.interest3_weight is not None:
            interests[user.interest3] = float(user.interest3_weight)
            subjects.add(user.interest3)
        
        profiles[user.name] = interests

    if not current_user_name:
        raise ValueError("The user requesting matches was not found or has an incomplete profile.")

    # 3. Run the Gale-Shapley and Cosine Similarity algorithm
    # We only care about the ranked recommendations list for the current user
    _, recommendations = recommend_gale_cosine(
        profiles=profiles,
        subjects=list(subjects),
        me=current_user_name
    )

    # 4. Shuffle the resulting preference list using Fisher-Yates
    shuffled_recommendations = fisher_yates_names(recommendations)

    # 5. Convert the shuffled list of names back to a list of UUIDs
    matched_ids = [user_name_to_id[name] for name in shuffled_recommendations]

    # 6. Store the final list in the database for the current user
    user_repo.update_user_matches(db=db, user_id=user_id, matched_ids=matched_ids)
    
    return matched_ids