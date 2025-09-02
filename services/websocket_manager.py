# services/websocket_manager.py

from fastapi import WebSocket
from typing import Dict
from uuid import UUID

class ConnectionManager:
    def __init__(self):
        # Dictionary to store active connections, mapping user_id to WebSocket object
        self.active_connections: Dict[UUID, WebSocket] = {}

    async def connect(self, user_id: UUID, websocket: WebSocket):
        """Accepts a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: UUID):
        """Closes and removes a WebSocket connection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_json(self, message: dict, user_id: UUID):
        """Sends a JSON message to a specific user if they are connected."""
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

# Create a single instance of the manager to be used across the application
manager = ConnectionManager()

