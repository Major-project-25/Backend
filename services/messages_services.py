# services/messages_services.py

from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from repositories import messages_repo
from model.messages import Message
from core.encryption import encrypt_message, decrypt_message
import hashlib

def send_message(db: Session, sender_id: UUID, receiver_id: UUID, content: Optional[str], media_url: Optional[str], message_type: str) -> Message:
    """
    Business logic for sending a message.
    Encrypts the content before saving if it exists.
    """
    if sender_id == receiver_id:
        raise ValueError("Sender and receiver cannot be the same person.")
    
    encrypted_content = None
    if content:
        # Only encrypt if there is text content
        encrypted_content = encrypt_message(content)
    
    return messages_repo.create_message(
        db, 
        sender_id=sender_id, 
        receiver_id=receiver_id, 
        content=encrypted_content,
        media_url=media_url,
        message_type=message_type
    )

def get_conversation(db: Session, user1_id: UUID, user2_id: UUID) -> List[Message]:
    """
    Business logic for retrieving a chat history.
    Decrypts messages after retrieving them.
    """
    encrypted_history = messages_repo.get_chat_history(db, user1_id, user2_id)
    
    for message in encrypted_history:
        if message.content:
            # Only decrypt if there is text content
            message.content = decrypt_message(message.content)
            
    return encrypted_history

def generate_meet_link(user1_id: UUID, user2_id: UUID) -> str:
    """
    Generates a consistent and functional Jitsi Meet link for two users.
    """
    ids = sorted([str(user1_id), str(user2_id)])
    room_name = hashlib.sha256("".join(ids).encode()).hexdigest()
    return f"https://meet.jit.si/KnowYourCampus-{room_name}"
