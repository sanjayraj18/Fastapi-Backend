from fastapi import FastAPI, WebSocket
import secrets
from roomregistry import RoomRegistry as registry

from connection import Connection, get_room

app = FastAPI()


@app.websocket("/ws/{room_id}/{user_id}")
async def endpoint(ws: WebSocket, room_id: str, user_id: str):
    await ws.accept()

    conn = Connection(
        id=secrets.token_hex(8),
        ws=ws,
        room_id=room_id,
        user_id=user_id,
    )

    registry.join(room_id, conn)
    conn.start() 

    try:
        if conn._reader_task:
            await conn._reader_task    
    finally:
        registry.leave(room_id, user_id) 