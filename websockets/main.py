from fastapi import FastAPI, WebSocket
import secrets
from roomregistry import RoomRegistry
from connection import Connection

app = FastAPI()
registry = RoomRegistry()          # ONE shared instance

@app.websocket("/ws/{room_id}/{user_id}")
async def endpoint(ws: WebSocket, room_id: str, user_id: str):
    await ws.accept()
    conn = Connection(id=secrets.token_hex(8), ws=ws,
                      room_id=room_id, user_id=user_id)
    registry.join(room_id, conn)   # creates room + consumer if new; sets conn.room
    conn.start()                   # launch reader + writer
    try:
        await conn.wait()          # hold open until disconnect
    finally:
        registry.leave(room_id, conn.id)   # removal + grace teardown