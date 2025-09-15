# api/v3/routes_msg.py
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from schema.messages import MessageCreate, MessageResponse, MeetLinkResponse
from services import messages_services, websocket_manager
from repositories import connections_repo
from DB.session import get_db, SessionLocal
# We need the decryption function here as well
from core.encryption import decrypt_message

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: UUID):
    """ The main real-time WebSocket endpoint for chat. """
    await websocket_manager.manager.connect(user_id, websocket)
    db: Session = SessionLocal()
    try:
        while True:
            data = await websocket.receive_json()
            message_data = MessageCreate.model_validate(data)
            
            # ... (Security check remains the same)
            are_connected = connections_repo.check_if_users_are_connected(
                db, user1_id=user_id, user2_id=message_data.receiver_id
            )
            if not are_connected:
                await websocket_manager.manager.send_json(
                    {"error": "You can only message your connections."}, user_id
                )
                continue

            # 1. Service layer encrypts and saves the message.
            # The returned `db_message` object has ENCRYPTED content.
            db_message = messages_services.send_message(
                db, 
                sender_id=user_id, 
                receiver_id=message_data.receiver_id, 
                content=message_data.content
            )

            # 2. Prepare the response to be sent over the WebSocket.
            # We must DECRYPT the content again before sending it.
            response_data = MessageResponse.model_validate(db_message).model_dump(mode="json")
            response_data['content'] = decrypt_message(db_message.content) # Explicitly decrypt for sending

            # 3. Send the DECRYPTED message to the recipient.
            await websocket_manager.manager.send_json(response_data, message_data.receiver_id)

    except WebSocketDisconnect:
        websocket_manager.manager.disconnect(user_id)
    except Exception as e:
        print(f"Error in websocket for user {user_id}: {e}")
    finally:
        db.close()

# --- HTTP Endpoints for Chat History and Video Calls ---

@router.get("/{user_id}/conversation/{other_user_id}", response_model=List[MessageResponse])
def get_message_history(user_id: UUID, other_user_id: UUID, db: Session = Depends(get_db)):
    """ Retrieves the chat history between the user and another user. """
    return messages_services.get_conversation(db, user1_id=user_id, user2_id=other_user_id)


@router.get("/{user_id}/meet/{other_user_id}", response_model=MeetLinkResponse)
def get_video_call_link(user_id: UUID, other_user_id: UUID):
    """ Generates a unique and consistent Google Meet link for a video call. """
    link = messages_services.generate_meet_link(user_id, other_user_id)
    return {"meet_link": link}


