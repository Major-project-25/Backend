# services/websocket_manager.py

from fastapi import WebSocket
from typing import Dict, List
from uuid import UUID
import logging
import asyncio

# Set up a logger for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Store multiple connections per user if they log in from multiple places (though your logic prevents this)
        self.active_connections: Dict[UUID, List[WebSocket]] = {}

    async def connect(self, user_id: UUID, websocket: WebSocket):
        """Accepts a new WebSocket connection."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"+++ WebSocket CONNECTED for user: {user_id}. Total users connected: {len(self.active_connections)}")

    def disconnect(self, user_id: UUID, websocket: WebSocket):
        """Closes and removes a specific WebSocket connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            logger.info(f"--- WebSocket DISCONNECTED for user: {user_id}. Total users connected: {len(self.active_connections)}")

    async def send_json(self, message: dict, user_id: UUID):
        """Sends a JSON message to a specific user if they are connected."""
        if user_id in self.active_connections:
            # Create a list of tasks to send the message to all connections for that user
            tasks = [conn.send_json(message) for conn in self.active_connections[user_id]]
            if tasks:
                logger.info(f"  -> SUCCESS: Found active connection(s) for {user_id}. Sending message.")
                await asyncio.gather(*tasks)
            else:
                 logger.warning(f"  -> FAILED: User {user_id} is in the list but has no active connections.")
        else:
            logger.warning(f"  -> FAILED: No active WebSocket connection found for user: {user_id}.")

# Create a single instance of the manager
manager = ConnectionManager()

