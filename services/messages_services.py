# Backend/services/messages_services.py

from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from repositories import messages_repo
from model.messages import Message
from core.encryption import encrypt_message, decrypt_message
import hashlib
import logging

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
    Retrieves the chat history between two users.
    Crucially, also marks all messages *to* user1 *from* user2 as read.
    """
    try:
        # --- 1. ADD THIS LINE ---
        # Mark all messages sent FROM other_user_id (user2_id) TO me (user1_id) as read
        messages_repo.mark_conversation_as_read(db, sender_id=user2_id, receiver_id=user1_id)

        # --- 2. The rest of the function is the same ---
        messages = messages_repo.get_conversation_history(db, user1_id, user2_id)
        
        # Decrypt content for sending to the client
        decrypted_messages = []
        for msg in messages:
            if msg.content:
                try:
                    msg.content = decrypt_message(msg.content)
                except Exception as e:
                    logging.warning(f"Failed to decrypt message {msg.id}: {e}")
                    msg.content = "[Message decryption failed]"
            decrypted_messages.append(msg)
            
        return decrypted_messages
        
    except Exception as e:
        logging.error(f"Error in get_conversation service: {e}")
        return []

def generate_meet_link(user1_id: UUID, user2_id: UUID) -> str:
    """
    Generates a consistent and functional Jitsi Meet link for two users.
    """
    ids = sorted([str(user1_id), str(user2_id)])
    room_name = hashlib.sha256("".join(ids).encode()).hexdigest()
    return f"https://meet.jit.si/KnowYourCampus-{room_name}"


# --- MODIFIED FUNCTION ---
def delete_message(db: Session, message_id: int, user_id: UUID) -> Message | None:
    """
    Business logic for deleting a message.
    Returns the deleted message object if successful, otherwise None.
    """
    deleted_message = messages_repo.delete_message_by_id(
        db, message_id=message_id, user_id=user_id
    )
    return deleted_message
