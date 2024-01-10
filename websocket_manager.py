from typing import List

from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from fastapi.routing import APIWebSocketRoute

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        if websocket not in self.active_connections:
            await self.connect(websocket)  # Connect if not already connected
        await websocket.send_text(message)

    async def broadcast(self, message):
        for connection in self.active_connections:
            try:
                await self.send_personal_message(message, connection)
            except Exception as e:
                print(f"Error broadcasting to a connection: {e}")

manager = ConnectionManager()

payload = ""
def set_payload(new_payload):
    global payload
    payload = new_payload

async def notify_clients(message: str):
    print(f"Trying to send data via websocket: {message}")
    await manager.broadcast(message)

async def handle_websocket(websocket: WebSocket, client_id: int):
    global payload
    
    await manager.connect(websocket)
    try:
        while True:
            print(payload)
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
            if payload != "":
                print(f"Trying to send data via websocket: {payload}")
                await manager.broadcast(payload)
                payload = ""
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")

websocket_route = APIWebSocketRoute("/ws/{client_id}", handle_websocket)
router.routes.append(websocket_route)