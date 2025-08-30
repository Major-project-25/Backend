# api/v1/routes_algo.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from DB.session import get_db
from services import user_services
from schema.algo_schema import MatchResponse

router = APIRouter()

@router.post("/match/{user_id}", response_model=MatchResponse) # CHANGED response_model
def generate_matches(user_id: UUID, db: Session = Depends(get_db)):
    """
    Triggers the matching process for a given user and returns the
    top 10 matches.
    """
    try:
        # This service function still generates and stores ALL matches
        matched_ids = user_services.generate_and_store_matches(db, user_id=user_id)
        
        if matched_ids is not None:
            # CHANGED: Return the first 10 matches in the new response format
            first_10_matches = matched_ids[:10]
            return {"matches": first_10_matches}
        else:
            # This handles cases where the user wasn't found or no matches could be made
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not generate matches for the user.",
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )