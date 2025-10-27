from sqlalchemy.orm import Session
from uuid import UUID
from repositories import user_repo
from schema.user_schema import UserCreate, AccountSetup
from typing import List, Dict
from model.user import User
from core.security import verify_password
from services.fisher_yates import fisher_yates_names # Corrected this import
import sys
import os
from datetime import datetime # Added datetime

# --- ANN IMPORT SETUP ---
SERVICES_DIR = os.path.dirname(os.path.abspath(__file__))
ANN_SRC_DIR = os.path.join(SERVICES_DIR, "ANN", "src")

if ANN_SRC_DIR not in sys.path:
    sys.path.append(ANN_SRC_DIR)

try:
    from matcher import get_top_k_from_users_flexible, expand_user_row_to_full
    print("[INFO] ANN Matcher imported successfully.")
except ImportError:
    print(f"Error: Could not import from ANN/src. Make sure {ANN_SRC_DIR} is correct.")
    get_top_k_from_users_flexible = None
    expand_user_row_to_full = None

CANONICAL_INTERESTS = [
    'artificial intelligence', 'machine learning', 'data science', 'hackathon',
    'full stack development', 'fintech', 'ui/ux design', 'cybersecurity',
    'web development', 'app development', 'cloud computing', 'deep learning',
    'robotics', 'research', 'blockchain', 'entrepreneurship',
    'vibecoding', 'collaboration', 'trading', 'product management'
]
# --- END: ANN IMPORT SETUP ---


def register_user_service(db: Session, user_data: UserCreate) -> User | None:
    """
    (This function is unchanged)
    """
    existing_user = user_repo.get_user_by_email(db, email=user_data.email)
    if existing_user:
        return None
    new_user = user_repo.create_user(db, user=user_data)
    return new_user

def authenticate_user_service(db: Session, login_data: UserCreate) -> User | None:
    """
    (This function is unchanged)
    """
    user = user_repo.get_user_by_email(db, email=login_data.email)
    if user and verify_password(login_data.password, user.password):
        return user
    return None

def setup_profile_service(db: Session, user_id: UUID, profile_data: AccountSetup) -> User | None:
    """
    (This function is unchanged)
    """
    existing_user = user_repo.get_user_by_reg_no(db, reg_no=profile_data.university_reg_no)
    if existing_user and existing_user.id != user_id:
        raise ValueError(f"University registration number '{profile_data.university_reg_no}' is already in use.")
    updated_user = user_repo.setup_user_account(
        db=db, user_id=user_id, profile_data=profile_data
    )
    return updated_user

def _format_user_interests(user: User) -> list[tuple[str, float]]:
    """
    (This function is corrected to return a list of tuples)
    """
    interests = [] 
    if user.interest1 and user.interest1_weight is not None:
        interests.append((user.interest1, float(user.interest1_weight)))
    if user.interest2 and user.interest2_weight is not None:
        interests.append((user.interest2, float(user.interest2_weight)))
    if user.interest3 and user.interest3_weight is not None:
        interests.append((user.interest3, float(user.interest3_weight)))
    return interests


# --- REPLACED: OLD 'generate_and_store_matches' IS REMOVED ---
# --- ADDED: NEW ANN-BASED FUNCTION ---
def generate_daily_matches_service(db: Session, user_id: UUID) -> List[UUID] | None:
    """
    Orchestrates the entire matching process for a given user using the ANN.
    1. Gets all eligible users.
    2. Runs the ANN model to get a ranked list of (Name, Score).
    3. Takes the Top 10 names.
    4. Shuffles the Top 10 names.
    5. Maps names back to UUIDs.
    6. Saves the *shuffled UUID list* and *today's date* to the DB.
    7. Returns the shuffled list of UUIDs.
    """
    if not get_top_k_from_users_flexible:
        raise ValueError("Matching service is unavailable. Could not import ANN model.")

    # 1. Fetch the current user
    current_user = user_repo.get_user_by_id(db, user_id)
    if not current_user:
        raise ValueError("User not found.")

    # 2. Fetch all eligible matches
    potential_matches = user_repo.get_potential_matches(db, user_id)
    today = datetime.utcnow().date()
    
    # If no potential matches, save an empty list for today and return
    if not potential_matches:
        user_repo.update_user_daily_matches(db, user_id, [], today)
        return []

    # 3. Format data AND create the Name -> ID map
    user_choices_list = _format_user_interests(current_user)

    users_rows_as_dicts = []
    user_name_to_id: Dict[str, UUID] = {}  # Map names to UUIDs

    for user in potential_matches:
        # Convert SQLAlchemy User object to a dictionary
        users_rows_as_dicts.append({
            "id": user.id,
            "name": user.name,
            "interest1": user.interest1,
            "interest1_weight": user.interest1_weight,
            "interest2": user.interest2,
            "interest2_weight": user.interest2_weight,
            "interest3": user.interest3,
            "interest3_weight": user.interest3_weight
        })
        # Store the name-to-ID mapping
        user_name_to_id[user.name] = user.id 
    
    # 4. Run the ANN Model
    # This returns a list of (Name, Score) tuples, as proven by our debugging
    ranked_matches = get_top_k_from_users_flexible(
        choices=user_choices_list, 
        users_rows=users_rows_as_dicts,
        k=len(users_rows_as_dicts), # Get all matches ranked
        interest_names=CANONICAL_INTERESTS
    )

    # 5. Take the top 10, extract names, and shuffle
    top_10_matches = ranked_matches[:10]
    
    # Get the names from the (Name, Score) tuples
    top_10_names = [match[0] for match in top_10_matches] 

    # Shuffle the list of names (Requirement #1)
    shuffled_names = fisher_yates_names(top_10_names)

    # Map shuffled names back to UUIDs
    shuffled_ids = [user_name_to_id[name] for name in shuffled_names]

    # 6. Store the final list of UUIDs (Step 4 & 5)
    # --- *** THIS IS THE CRITICAL FIX *** ---
    # We must pass 'generation_date=today' so the list is saved for the day.
    user_repo.update_user_daily_matches(
        db=db,
        user_id=user_id,
        daily_matches=shuffled_ids, # This is now a list of UUIDs
        generation_date=today
    )
    # --- *** END OF FIX *** ---
    
    return shuffled_ids

