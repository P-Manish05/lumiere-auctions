from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # Maps auction_id to a list of active WebSocket connections
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, auction_id: int):
        await websocket.accept()
        if auction_id not in self.active_connections:
            self.active_connections[auction_id] = []
        self.active_connections[auction_id].append(websocket)

    def disconnect(self, websocket: WebSocket, auction_id: int):
        if auction_id in self.active_connections:
            if websocket in self.active_connections[auction_id]:
                self.active_connections[auction_id].remove(websocket)
            if not self.active_connections[auction_id]:
                del self.active_connections[auction_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast_to_auction(self, auction_id: int, message: dict):
        if auction_id in self.active_connections:
            for connection in self.active_connections[auction_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    # Connection might have died, handle clean-up if needed,
                    # but typically handled during disconnect.
                    pass

manager = ConnectionManager()
