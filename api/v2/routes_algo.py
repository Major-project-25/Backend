from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from DB.session import get_db
from services import user_services
from repositories import user_repo, connections_repo
from schema.algo_schema import MatchResponse
from datetime import date, datetime # <--- IMPORT ADDED

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
        # 1. Get the user from the database (Unchanged)
        user = user_repo.get_user_by_id(db, user_id=user_id)
        if not user:
             raise HTTPException(
                 status_code=status.HTTP_404_NOT_FOUND,
                 detail="User not found.",
             )

        # --- *** THIS IS THE FINAL FIX *** ---
        # Use UTC date for consistent comparison with the service layer
        today = datetime.utcnow().date()
        # --- *** END OF FIX *** ---

        daily_matches_list = []

        # 2. Check if matches were generated today (Unchanged)
        #    (Use your exact column name: 'matches_generated_at')
        #    Now this comparison will work correctly (UTC vs UTC)
        if user.matches_generated_at == today and user.daily_matches:
            # Matches already exist for today. Use the stored list. (Unchanged)
            daily_matches_list = user.daily_matches

        else:
            # First time today. Generate new matches using the new ANN service. (Unchanged)
            # This service does all the work: ANN, shuffle, save (with UTC date), and returns the list.
            daily_matches_list = user_services.generate_daily_matches_service(db, user_id=user_id)
            # Handle case where service returns None (e.g., error during generation)
            if daily_matches_list is None:
                 raise HTTPException(
                     status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                     detail="Failed to generate matches.",
                 )


        # 3. Filter the daily list (This entire block is unchanged and will now work)
        # Now, we filter out anyone the user already has an 'accepted' or 'pending'
        # connection with (in either direction).

        # Get all "accepted" connections
        accepted_conns = connections_repo.get_accepted_connections(db, user_id=user_id)
        # Get all "pending" requests sent *by* the user
        pending_sent = connections_repo.get_pending_requests_sent_by_user(db, user_id=user_id)
        # Get all "pending" requests sent *to* the user (received by them)
        pending_received = connections_repo.get_pending_requests(db, user_id=user_id)

        # Create a set of all user IDs to ignore (Unchanged)
        consumed_user_ids = set()
        for conn in accepted_conns:
            # Add both users from an accepted connection
            if conn.requester_id != user_id:
                 consumed_user_ids.add(conn.requester_id)
            if conn.addressee_id != user_id:
                 consumed_user_ids.add(conn.addressee_id)
        for req in pending_sent:
            consumed_user_ids.add(req.addressee_id) # The person they sent the request to
        for req in pending_received:
            consumed_user_ids.add(req.requester_id) # The person who sent the request to them

        # Create the final list, filtering out consumed IDs and the user themself (Unchanged)
        remaining_matches = [
            match_uuid for match_uuid in daily_matches_list
            if match_uuid not in consumed_user_ids and match_uuid != user_id
        ]

        # Ensure the response schema matches {"matches": [...]}
        return {"matches": remaining_matches}

    except ValueError as ve:
        # This now catches errors from our new service (Unchanged)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve),
        )
    except Exception as e:
        # (Unchanged)
        # You should log the exception 'e' here for debugging
        print(f"ERROR in get_daily_matches: {e}") # Added basic print for debugging
        import traceback
        traceback.print_exc() # Print full traceback
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}",
        )

