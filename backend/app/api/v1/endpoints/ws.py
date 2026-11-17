from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.websocket_manager import manager
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.websocket("/ws/{project_id}")
async def websocket_project_endpoint(websocket: WebSocket, project_id: str):
    await manager.connect(project_id, websocket)
    try:
        while True:
            # Keep connection alive & listen for client pings or local broadcasts
            data = await websocket.receive_text()
            # Echo heartbeat or log
            logger.debug(f"Received WS message on project {project_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(project_id, websocket)
    except Exception as e:
        logger.error(f"WebSocket error on project {project_id}: {e}")
        manager.disconnect(project_id, websocket)
