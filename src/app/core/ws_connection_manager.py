import uuid
from typing import Dict
from fastapi import WebSocket

from src.app.core.config import settings


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str] = {}
        self.recording_files: Dict[str, str] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket

        # Create UUID for this recording session
        audio_uuid = str(uuid.uuid4())
        self.recording_files[client_id] = f"{settings.MEDIA_DIR_PATH}/{audio_uuid}.webm"

        # Send UUID back to client immediately
        await websocket.send_json({"event_type": "audio_uuid", "uuid": audio_uuid})

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            self.active_connections.pop(client_id)
            if client_id in self.recording_files:
                self.recording_files.pop(client_id)
