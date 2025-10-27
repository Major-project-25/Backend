# api/v3/routes_msg.py
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
import os
import uuid 
import aiofiles 
from typing import List
from schema.messages import MessageCreate, MessageResponse, MeetLinkResponse, MediaUploadResponse
from services import messages_services, websocket_manager, moderation_service
from repositories import connections_repo, user_repo, messages_repo
from DB.session import get_db, SessionLocal
from core.encryption import decrypt_message

router = APIRouter()

@router.post("/upload-media", response_model=MediaUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_media_file(file: UploadFile = File(...)):
    """
    Handles uploading image or video files for chat.
    Saves the file and returns its web-accessible URL.
    This endpoint uses aiofiles to stream the file asynchronously.
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    CHAT_MEDIA_DIR = os.path.join(BASE_DIR, "static", "chat_media")

    file_extension = os.path.splitext(file.filename)[1]
    
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(CHAT_MEDIA_DIR, unique_filename)

    try:
        # --- 4. IMPLEMENTED YOUR AIOFILES SOLUTION ---
        async with aiofiles.open(file_path, "wb") as buffer:
            # Read the file in 1MB chunks asynchronously
            while True:
                chunk = await file.read(1024 * 1024) # 1 MB
                if not chunk:
                    break
                await buffer.write(chunk)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")
    finally:
        await file.close() # Always close the file stream

    media_url = f"/static/chat_media/{unique_filename}"
    return {"media_url": media_url}


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: UUID):
    """ The main real-time WebSocket endpoint for chat. """
    await websocket_manager.manager.connect(user_id, websocket)
    try:
        while True:
            # Create a new database session for each message
            db: Session = SessionLocal()
            try:
                data = await websocket.receive_json()
                
                # --- 2. ADD THIS NEW LOGIC BLOCK ---
                message_type = data.get("type")

                if message_type == "read_ack":
                    # This is a 'message read' acknowledgment from the client
                    message_id = data.get("message_id")
                    if message_id:
                        # Call repo function to mark this specific message as read
                        # We use user_id (the connected user) as the current_user_id
                        messages_repo.mark_message_as_read_by_id(db, message_id, user_id)
                    
                    continue # Skip the rest of the loop, it was just an ack
                
                # --- 3. This 'if' is your existing logic ---
                # If no type, or a different type (like 'text'), it's a new chat message.
                # We validate it against the MessageCreate schema
                
                message_data = MessageCreate.model_validate(data)
                
                # ... (rest of your existing logic for moderation) ...
                if message_data.content and moderation_service.is_message_offensive(message_data.content):
                    await websocket_manager.manager.send_json({
                        "type": "moderation_warning",
                        "message": "Your message was not sent because it was flagged as potentially offensive."
                    }, user_id)
                    continue
                
                # ... (rest of your existing logic for checking connection) ...
                are_connected = connections_repo.check_if_users_are_connected(
                    db, user1_id=user_id, user2_id=message_data.receiver_id
                )
                if not are_connected:
                    await websocket_manager.manager.send_json(
                        {"error": "You can only message your connections."}, user_id
                    )
                    continue

                # ... (rest of your existing logic for saving and sending) ...
                db_message = messages_services.send_message(
                    db, 
                    sender_id=user_id, 
                    receiver_id=message_data.receiver_id, 
                    content=message_data.content,
                    media_url=message_data.media_url,
                    message_type=message_data.message_type
                )
                
                response_data = MessageResponse.model_validate(db_message).model_dump(mode="json")
                if response_data['content']:
                    response_data['content'] = decrypt_message(db_message.content)
                
                await websocket_manager.manager.send_json(response_data, message_data.receiver_id)
                await websocket_manager.manager.send_json(response_data, user_id)

            finally:
                # Close the session for the current message
                db.close()

    except WebSocketDisconnect:
        websocket_manager.manager.disconnect(user_id, websocket)
    except Exception as e:
        print(f"Error in websocket for user {user_id}: {e}")
        websocket_manager.manager.disconnect(user_id, websocket)


# --- HTTP ENDPOINT TO DELETE A MESSAGE ---
@router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_message(message_id: int, user_id: UUID, db: Session = Depends(get_db)):
    """
    Deletes a specific chat message and notifies both users via WebSocket.
    A user can only delete a message they have sent.
    """
    deleted_message = messages_services.delete_message(
        db, message_id=message_id, user_id=user_id
    )

    if not deleted_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found or you do not have permission to delete it.",
        )
    
    # --- REAL-TIME NOTIFICATION LOGIC ---
    # Create the notification payload
    notification = {
        "type": "message_deleted",
        "message_id": message_id
    }
    
    # Notify both the sender and the receiver
    sender_id = deleted_message.sender_id
    receiver_id = deleted_message.receiver_id
    
    await websocket_manager.manager.send_json(notification, sender_id)
    await websocket_manager.manager.send_json(notification, receiver_id)
    
    # A 204 response does not have a body, so we return nothing.
    return


# --- HTTP ENDPOINTS FOR CHAT HISTORY AND VIDEO CALLS ---
@router.get("/{user_id}/conversation/{other_user_id}", response_model=List[MessageResponse])
def get_message_history(user_id: UUID, other_user_id: UUID, db: Session = Depends(get_db)):
    """ Retrieves the chat history between the user and another user. """
    return messages_services.get_conversation(db, user1_id=user_id, user2_id=other_user_id)


@router.get("/{user_id}/meet/{other_user_id}", response_model=MeetLinkResponse)
async def get_video_call_link(user_id: UUID, other_user_id: UUID, db: Session = Depends(get_db)):
    """ 
    Generates a unique Meet link and sends a real-time notification 
    to the other user.
    """
    caller = user_repo.get_user_by_id(db, user_id)
    if not caller:
        raise HTTPException(status_code=404, detail="Caller not found.")

    link = messages_services.generate_meet_link(user_id, other_user_id)
    
    notification_payload = {
        "type": "video_call_invitation",
        "meet_link": link,
        "caller_name": caller.name or "A user"
    }
    
    # Push the notification to the other user via WebSocket
    await websocket_manager.manager.send_json(notification_payload, other_user_id)
    
    return {"meet_link": link}

