# repositories/connections_repo.py

from sqlalchemy.orm import Session
from sqlalchemy import or_
from uuid import UUID
from typing import List
from model.connections import Connection

def create_connection_request(db: Session, requester_id: UUID, addressee_id: UUID) -> Connection:
    db_connection = Connection(requester_id=requester_id, addressee_id=addressee_id, status='pending')
    db.add(db_connection)
    db.commit()
    db.refresh(db_connection)
    return db_connection

def get_pending_requests(db: Session, user_id: UUID) -> List[Connection]:
    return db.query(Connection).filter(
        Connection.addressee_id == user_id,
        Connection.status == 'pending'
    ).all()

def get_connection(db: Session, requester_id: UUID, addressee_id: UUID) -> Connection | None:
    return db.query(Connection).filter_by(requester_id=requester_id, addressee_id=addressee_id).first()

def update_connection_status(db: Session, connection: Connection, new_status: str) -> Connection:
    connection.status = new_status
    db.commit()
    db.refresh(connection)
    return connection

def get_accepted_connections(db: Session, user_id: UUID) -> List[Connection]:
    return db.query(Connection).filter(
        or_(Connection.requester_id == user_id, Connection.addressee_id == user_id),
        Connection.status == 'accepted'
    ).all()

def check_if_users_are_connected(db: Session, user1_id: UUID, user2_id: UUID) -> bool:
    """ Checks if an 'accepted' connection exists between two users. """
    connection = db.query(Connection).filter(
        or_(
            (Connection.requester_id == user1_id) & (Connection.addressee_id == user2_id),
            (Connection.requester_id == user2_id) & (Connection.addressee_id == user1_id)
        ),
        Connection.status == 'accepted'
    ).first()
    return connection is not None