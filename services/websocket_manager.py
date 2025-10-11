from fastapi import WebSocket
from typing import Dict
from uuid import UUID
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID, WebSocket] = {}

    async def connect(self, user_id: UUID, websocket: WebSocket):
        """Accepts and stores a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"+++ WebSocket CONNECTED for user: {user_id}. Total connections: {len(self.active_connections)}")

    def disconnect(self, user_id: UUID):
        """Removes a WebSocket connection from the active pool."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"--- WebSocket DISCONNECTED for user: {user_id}. Total connections: {len(self.active_connections)}")

    async def send_json(self, message: dict, user_id: UUID):
        """Sends a JSON message to a specific connected user."""
        logger.info(f">>> Attempting to send message to user: {user_id}")
        if user_id in self.active_connections:
            logger.info(f"    User {user_id} FOUND in active connections. Sending...")
            websocket = self.active_connections[user_id]
            try:
                await websocket.send_json(message)
                logger.info(f"    Message sent successfully to {user_id}.")
            except Exception as e:
                logger.error(f"    !!! ERROR sending message to {user_id}: {e}")
                # If sending fails, the connection is likely dead. Clean it up.
                self.disconnect(user_id)
        else:
            logger.warning(f"    !!! User {user_id} NOT FOUND in active connections.")
            logger.warning(f"    Current active users: {list(self.active_connections.keys())}")

# A single, shared instance of the manager for the whole application
manager = ConnectionManager()
