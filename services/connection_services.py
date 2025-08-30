# services/connection_services.py

from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from repositories import connections_repo
from model.connections import Connection

def send_request(db: Session, requester_id: UUID, addressee_id: UUID) -> Connection:
    # Logic to prevent duplicate requests or connecting to oneself can be added here
    if requester_id == addressee_id:
        raise ValueError("Cannot send a connection request to yourself.")
    
    existing = connections_repo.get_connection(db, requester_id, addressee_id)
    if existing:
        raise ValueError("Connection request already sent.")
        
    return connections_repo.create_connection_request(db, requester_id, addressee_id)

def view_pending_requests(db: Session, user_id: UUID) -> List[Connection]:
    return connections_repo.get_pending_requests(db, user_id)

def respond_to_request(db: Session, requester_id: UUID, addressee_id: UUID, new_status: str) -> Connection:
    connection = connections_repo.get_connection(db, requester_id, addressee_id)
    if not connection or connection.addressee_id != addressee_id or connection.status != 'pending':
        raise ValueError("No pending request found to respond to.")
        
    if new_status not in ['accepted', 'declined']:
        raise ValueError("Invalid status. Must be 'accepted' or 'declined'.")

    return connections_repo.update_connection_status(db, connection, new_status)

def view_friends(db: Session, user_id: UUID) -> List[Connection]:
    return connections_repo.get_accepted_connections(db, user_id)