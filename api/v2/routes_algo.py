# api/v1/routes_algo.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from DB.session import get_db
from services import user_services
from repositories import user_repo, connections_repo 
from schema.algo_schema import MatchResponse
from datetime import date

router = APIRouter()

@router.post("/match/{user_id}", response_model=MatchResponse)
def get_daily_matches(user_id: UUID, db: Session = Depends(get_db)):
    """
    Triggers the matching process for a given user.
    - If it's the first request of the day, generates a new static list of 10 matches.
    - If matches for the day already exist, returns the remaining users from that list
      (filtering out those already connected or with pending requests).
    """
    try:
        # 1. Get the user from the database
        user = user_repo.get_user_by_id(db, user_id=user_id)
        if not user:
             raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        today = date.today()
        daily_matches_list = []

        # 2. Check if matches were generated today
        #    (Use your exact column name: 'matches_generated_at')
        if user.matches_generated_at == today and user.daily_matches:
            # Matches already exist for today. Use the stored list.
            daily_matches_list = user.daily_matches
            
        else:
            # First time today. Generate new matches.
            # This service function generates and stores the FULL match pool
            # in the 'matched_profiles' column.
            full_match_pool = user_services.generate_and_store_matches(db, user_id=user_id)
            
            if full_match_pool is None:
                 raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Could not generate matches for the user.",
                )
            
            # Get the top 10 for the day
            daily_matches_list = full_match_pool[:10]
            
            # Save this daily list and the date to the user's profile
            user_repo.update_user_daily_matches(
                db, 
                user_id=user_id, 
                daily_matches=daily_matches_list, 
                generation_date=today
            )

        # 3. Filter the daily list
        # Now, we filter out anyone the user already has an 'accepted' or 'pending'
        # connection with (in either direction).
        
        # Get all "accepted" connections
        accepted_conns = connections_repo.get_accepted_connections(db, user_id=user_id)
        # Get all "pending" requests sent *by* the user
        pending_sent = connections_repo.get_pending_requests_sent_by_user(db, user_id=user_id)
        # Get all "pending" requests sent *to* the user (received by them)
        pending_received = connections_repo.get_pending_requests(db, user_id=user_id)

        # Create a set of all user IDs to ignore
        consumed_user_ids = set()
        for conn in accepted_conns:
            consumed_user_ids.add(conn.requester_id)
            consumed_user_ids.add(conn.addressee_id)
        for req in pending_sent:
            consumed_user_ids.add(req.addressee_id) # The person they sent the request to
        for req in pending_received:
            consumed_user_ids.add(req.requester_id) # The person who sent the request to them
        
        # Create the final list, filtering out consumed IDs and the user themself
        remaining_matches = [
            match_uuid for match_uuid in daily_matches_list 
            if match_uuid not in consumed_user_ids and match_uuid != user_id
        ]

        return {"matches": remaining_matches}
            
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve),
        )
    except Exception as e:
        # You should log the exception 'e' here for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )