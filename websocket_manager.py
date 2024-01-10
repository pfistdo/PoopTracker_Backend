import json

from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from fastapi.routing import APIWebSocketRoute

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        print(f"Trying to send data via WebSocket: {message}")
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_payload = {"type": "message", "message": data, "client_id": client_id}
            message_payload_json = json.dumps(message_payload)
            await manager.broadcast(message_payload_json)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

websocket_route = APIWebSocketRoute("/ws/{client_id}", websocket_endpoint)
router.routes.append(websocket_route)