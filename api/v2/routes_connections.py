# api/v2/routes_connections.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from DB.session import get_db
from schema.connections import ConnectionRequest, ConnectionUpdate, StatusResponse, PendingRequestDetail, FriendsResponse
from services import connection_services
from repositories import user_repo # Import user_repo to get user details

router = APIRouter()

@router.post("/request", status_code=status.HTTP_201_CREATED, response_model=StatusResponse)
def send_connection_request(user_id: UUID, req: ConnectionRequest, db: Session = Depends(get_db)):
    """ 1. Sending a Connection Request """
    try:
        # Get the addressee's details to include their USN in the response
        addressee = user_repo.get_user_by_id(db, user_id=req.addressee_id)
        if not addressee:
            raise ValueError("User to connect with not found.")

        connection_services.send_request(db, requester_id=user_id, addressee_id=req.addressee_id)
        
        return {"message": f"Connection request has been sent to {addressee.university_reg_no}"}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{user_id}/requests/pending", response_model=List[PendingRequestDetail])
def view_received_requests(user_id: UUID, db: Session = Depends(get_db)):
    """ 2. Viewing Received (Pending) Requests """
    pending_connections = connection_services.view_pending_requests(db, user_id=user_id)
    
    # Transform the full user object into the desired response model
    response = []
    for conn in pending_connections:
        requester_details = PendingRequestDetail.model_validate(conn.requester)
        # We need to manually add the requester_id since it's not in the User model
        requester_details.requester_id = conn.requester_id
        response.append(requester_details)
        
    return response

@router.put("/{user_id}/requests/respond", status_code=status.HTTP_204_NO_CONTENT)
def respond_to_connection_request(user_id: UUID, update: ConnectionUpdate, db: Session = Depends(get_db)):
    """ 3. Accepting or Declining a Request (No Response Body) """
    try:
        connection_services.respond_to_request(
            db, 
            requester_id=update.requester_id, 
            addressee_id=user_id,
            new_status=update.new_status
        )
        return  # FastAPI will automatically return a 204 No Content response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get("/{user_id}/friends", response_model=FriendsResponse)
def view_all_accepted_connections(user_id: UUID, db: Session = Depends(get_db)):
    """ 4. Viewing All Accepted Connections (Friends) """
    connections = connection_services.view_friends(db, user_id=user_id)
    
    usns = []
    for conn in connections:
        # Get the USN of the *other* person in the connection
        if conn.requester_id == user_id:
            if conn.addressee.university_reg_no:
                usns.append(conn.addressee.university_reg_no)
        else:
            if conn.requester.university_reg_no:
                usns.append(conn.requester.university_reg_no)
                
    return {"usns": usns}