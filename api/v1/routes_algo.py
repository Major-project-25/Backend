# api/v1/routes_algo.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from DB.session import get_db
from services import user_services
from schema.user_schema import StatusResponse

router = APIRouter()

@router.post("/match/{user_id}", response_model=StatusResponse)
def generate_matches(user_id: UUID, db: Session = Depends(get_db)):
    """
    Triggers the matching process for a given user.
    - Fetches all user profiles.
    - Runs Gale-Shapley + Cosine Similarity to get a preference list.
    - Shuffles the list with Fisher-Yates.
    - Stores the final matched list in the user's profile.
    """
    try:
        matched_ids = user_services.generate_and_store_matches(db, user_id=user_id)
        if matched_ids is not None:
            return {"message": f"Successfully generated and stored {len(matched_ids)} matches."}
        else:
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not generate matches for the user.",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )