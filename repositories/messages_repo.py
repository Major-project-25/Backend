# repositories/messages_repo.py

from sqlalchemy.orm import Session
from sqlalchemy import or_
from uuid import UUID
from typing import List
from model.messages import Message

def create_message(db: Session, sender_id: UUID, receiver_id: UUID, content: str) -> Message:
    """ Creates and saves a new message to the database. """
    db_message = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_chat_history(db: Session, user1_id: UUID, user2_id: UUID) -> List[Message]:
    """ Retrieves all messages between two users, ordered by time. """
    return db.query(Message).filter(
        or_(
            (Message.sender_id == user1_id) & (Message.receiver_id == user2_id),
            (Message.sender_id == user2_id) & (Message.receiver_id == user1_id)
        )
    ).order_by(Message.timestamp.asc()).all()

