# api/v3/routes_msg.py
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
import shutil
import os
import uuid # <-- 1. IMPORT THE UUID LIBRARY
from typing import List
from schema.messages import MessageCreate, MessageResponse, MeetLinkResponse, MediaUploadResponse
from services import messages_services, websocket_manager, moderation_service
from repositories import connections_repo, user_repo
from DB.session import get_db, SessionLocal
from core.encryption import decrypt_message

router = APIRouter()

# --- HTTP ENDPOINT FOR MEDIA UPLOADS ---
@router.post("/upload-media", response_model=MediaUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_media_file(file: UploadFile = File(...)):
    """
    Handles uploading image or video files for chat.
    Saves the file and returns its web-accessible URL.
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    CHAT_MEDIA_DIR = os.path.join(BASE_DIR, "static", "chat_media")

    file_extension = os.path.splitext(file.filename)[1]
    
    # --- 2. THIS IS THE CORRECTED LINE ---
    # Generate a standard random UUID for the filename.
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    # ------------------------------------

    file_path = os.path.join(CHAT_MEDIA_DIR, unique_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

    media_url = f"/static/chat_media/{unique_filename}"
    return {"media_url": media_url}


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: UUID):
    """ The main real-time WebSocket endpoint for chat. """
    await websocket_manager.manager.connect(user_id, websocket)
    try:
        while True:
            db: Session = SessionLocal()
            try:
                data = await websocket.receive_json()
                message_data = MessageCreate.model_validate(data)
                
                if message_data.content and moderation_service.is_message_offensive(message_data.content):
                    await websocket_manager.manager.send_json({
                        "type": "moderation_warning",
                        "message": "Your message was not sent because it was flagged as potentially offensive."
                    }, user_id)
                    continue
                
                are_connected = connections_repo.check_if_users_are_connected(
                    db, user1_id=user_id, user2_id=message_data.receiver_id
                )
                if not are_connected:
                    await websocket_manager.manager.send_json(
                        {"error": "You can only message your connections."}, user_id
                    )
                    continue

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
                db.close()

    except WebSocketDisconnect:
        websocket_manager.manager.disconnect(user_id)
    except Exception as e:
        print(f"Error in websocket for user {user_id}: {e}")


# --- HTTP Endpoints (Unchanged) ---
@router.get("/{user_id}/conversation/{other_user_id}", response_model=List[MessageResponse])
def get_message_history(user_id: UUID, other_user_id: UUID, db: Session = Depends(get_db)):
    return messages_services.get_conversation(db, user1_id=user_id, user2_id=other_user_id)


@router.get("/{user_id}/meet/{other_user_id}", response_model=MeetLinkResponse)
async def get_video_call_link(user_id: UUID, other_user_id: UUID, db: Session = Depends(get_db)):
    caller = user_repo.get_user_by_id(db, user_id)
    if not caller:
        return {"error": "Caller not found."}
    link = messages_services.generate_meet_link(user_id, other_user_id)
    notification_payload = {
        "type": "video_call_invitation",
        "meet_link": link,
        "caller_name": caller.name or "A user"
    }
    await websocket_manager.manager.send_json(notification_payload, other_user_id)
    return {"meet_link": link}

