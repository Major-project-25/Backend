# Backend/repositories/messages_repo.py

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, update
from uuid import UUID
from typing import List, Optional
from model.messages import Message
import os # <-- 1. IMPORT OS FOR FILE OPERATIONS
import logging

def create_message(db: Session, sender_id: UUID, receiver_id: UUID, content: Optional[str], media_url: Optional[str], message_type: str) -> Message:
    """ Creates and saves a new message to the database. """
    db_message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content,
        media_url=media_url,
        message_type=message_type
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_conversation_history(db: Session, user1_id: UUID, user2_id: UUID) -> List[Message]:
    """
    Retrieves all messages between two users, ordered by timestamp.
    """
    try:
        # Query that finds messages where the pair matches (sender, receiver) OR (receiver, sender)
        messages = db.query(Message).filter(
            or_(
                and_(Message.sender_id == user1_id, Message.receiver_id == user2_id),
                and_(Message.sender_id == user2_id, Message.receiver_id == user1_id)
            )
        ).order_by(Message.timestamp.asc()).all()
        
        return messages
    
    except Exception as e:
        logging.error(f"Error retrieving conversation history: {e}")
        db.rollback()
        return []


# --- THIS FUNCTION IS NOW MODIFIED ---
def delete_message_by_id(db: Session, message_id: int, user_id: UUID) -> Message | None:
    """
    Deletes a message by its ID, but only if the user requesting the deletion
    is the original sender of the message.

    If the message contains media, it also deletes the associated file from the server.
    """
    message_to_delete = db.query(Message).filter(
        and_(
            Message.id == message_id,
            Message.sender_id == user_id
        )
    ).first()

    if not message_to_delete:
        return None # Message not found or user is not the sender

    # --- 2. ADD THIS NEW LOGIC TO DELETE THE FILE ---
    if message_to_delete.media_url:
        try:
            # Construct the absolute path to the file
            # We go up two directories to get to the 'Backend' root
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # media_url is like '/static/chat_media/file.jpg', lstrip('/')
            # removes the leading '/' so os.path.join works correctly
            file_path = os.path.join(BASE_DIR, message_to_delete.media_url.lstrip('/'))

            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted media file: {file_path}")
            else:
                print(f"Warning: File not found, but deleting DB record: {file_path}")
        except Exception as e:
            # Log the error, but don't stop the DB deletion
            print(f"Error deleting file {message_to_delete.media_url}: {e}")
    # --- END OF NEW LOGIC ---

    # Delete the message record from the database
    db.delete(message_to_delete)
    db.commit()

    return message_to_delete

def get_unread_message_count(db: Session, sender_id: UUID, receiver_id: UUID) -> int:
    """
    Counts unread messages sent from a specific sender to a specific receiver.
    """
    count = db.query(func.count(Message.id)).filter(
        Message.sender_id == sender_id,
        Message.receiver_id == receiver_id,
        Message.is_read == False
    ).scalar()
    return count or 0

def mark_conversation_as_read(db: Session, sender_id: UUID, receiver_id: UUID):
    """
    Marks all unread messages FROM sender_id TO receiver_id as read.
    """
    try:
        # Create an update statement
        stmt = (
            update(Message)
            .where(
                and_(
                    Message.sender_id == sender_id,
                    Message.receiver_id == receiver_id,
                    Message.is_read == False
                )
            )
            .values(is_read=True)
            .execution_options(synchronize_session=False) # Important for efficiency
        )
        
        db.execute(stmt)
        db.commit()
        
    except Exception as e:
        logging.error(f"Error marking conversation as read: {e}")
        db.rollback()

def mark_message_as_read_by_id(db: Session, message_id: int, current_user_id: UUID):
    """
    Marks a specific message as read, only if the user is the receiver.
    This is triggered by a WebSocket 'read_ack'.
    """
    try:
        # Find the specific message
        message = db.query(Message).filter(
            and_(
                Message.id == message_id,
                Message.receiver_id == current_user_id, # Security: User must be the receiver
                Message.is_read == False
            )
        ).first()

        if message:
            message.is_read = True
            db.commit()
            
    except Exception as e:
        logging.error(f"Error marking single message as read: {e}")
        db.rollback()
