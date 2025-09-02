# services/messages_services.py

from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from repositories import messages_repo
from model.messages import Message

def send_message(db: Session, sender_id: UUID, receiver_id: UUID, content: str) -> Message:
    """ Business logic for sending a message. """
    if sender_id == receiver_id:
        raise ValueError("Sender and receiver cannot be the same person.")
    
    return messages_repo.create_message(db, sender_id=sender_id, receiver_id=receiver_id, content=content)

def get_conversation(db: Session, user1_id: UUID, user2_id: UUID) -> List[Message]:
    """ Business logic for retrieving a chat history. """
    return messages_repo.get_chat_history(db, user1_id, user2_id)

def generate_meet_link(user1_id: UUID, user2_id: UUID) -> str:
    """
    Generates a consistent Google Meet link for two users.
    Sorting the UUIDs ensures both users always get the same link.
    """
    # Sort UUIDs to ensure the room name is always the same regardless of who initiates
    ids = sorted([str(user1_id), str(user2_id)])
    room_name = "".join(ids).replace("-", "")
    return f"https://meet.google.com/lookup/{room_name}"

