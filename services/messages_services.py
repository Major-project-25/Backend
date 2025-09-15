# services/messages_services.py

from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from repositories import messages_repo
from model.messages import Message
from core.encryption import encrypt_message, decrypt_message # Import the new functions
import hashlib

def send_message(db: Session, sender_id: UUID, receiver_id: UUID, content: str) -> Message:
    """
    Business logic for sending a message.
    Encrypts the content before saving.
    """
    if sender_id == receiver_id:
        raise ValueError("Sender and receiver cannot be the same person.")
    
    # Encrypt the content before it goes to the repository
    encrypted_content = encrypt_message(content)
    
    return messages_repo.create_message(db, sender_id=sender_id, receiver_id=receiver_id, content=encrypted_content)

def get_conversation(db: Session, user1_id: UUID, user2_id: UUID) -> List[Message]:
    """
    Business logic for retrieving a chat history.
    Decrypts messages after retrieving them.
    """
    # 1. Get the encrypted history from the database
    encrypted_history = messages_repo.get_chat_history(db, user1_id, user2_id)
    
    # 2. Decrypt each message's content before sending it to the user
    for message in encrypted_history:
        message.content = decrypt_message(message.content)
        
    return encrypted_history

def generate_meet_link(user1_id: UUID, user2_id: UUID) -> str:
    """
    Generates a consistent and functional Jitsi Meet link for two users.
    """
    ids = sorted([str(user1_id), str(user2_id)])
    room_name = hashlib.sha256("".join(ids).encode()).hexdigest()
    return f"https://meet.jit.si/KnowYourCampus-{room_name}"