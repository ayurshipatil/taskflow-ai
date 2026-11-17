from typing import Dict, List
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Maps project_id -> list of active WebSockets
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, project_id: str, websocket: WebSocket):
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        self.active_connections[project_id].append(websocket)
        logger.info(f"WebSocket connected to project {project_id}. Total: {len(self.active_connections[project_id])}")

    def disconnect(self, project_id: str, websocket: WebSocket):
        if project_id in self.active_connections:
            if websocket in self.active_connections[project_id]:
                self.active_connections[project_id].remove(websocket)
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]
        logger.info(f"WebSocket disconnected from project {project_id}")

    async def broadcast(self, project_id: str, message: dict):
        if project_id in self.active_connections:
            data = json.dumps(message)
            for connection in list(self.active_connections[project_id]):
                try:
                    await connection.send_text(data)
                except Exception as e:
                    logger.error(f"Error broadcasting to client: {e}")
                    self.disconnect(project_id, connection)

manager = ConnectionManager()
