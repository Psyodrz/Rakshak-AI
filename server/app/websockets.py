
from fastapi import WebSocket
from typing import List, Dict, Any
import json
from datetime import datetime
from .utils.logger import logger

class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts events.
    
    Features:
    - Track active connections
    - Broadcast JSON messages
    - Handle disconnects gracefully
    """
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Active connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message(
            {
                "type": "CONNECTION_ESTABLISHED",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Connected to RAKSHAK-AI Real-time Bus"
            },
            websocket
        )

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Active connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        logger.info(f"Broadcasting event: {message.get('type')}")
        
        # Add server timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()
            
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to client: {e}")
                disconnected.append(connection)
        
        # Clean up dead connections
        for dead in disconnected:
            self.disconnect(dead)

# Global instance
manager = ConnectionManager()
