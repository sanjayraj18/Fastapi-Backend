from fastapi import FastAPI, WebSocket
import secrets

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
    room = get_room(room_id)
    room.add(conn)
    print(f"[{room_id}] + {conn.id} {user_id} ({len(room)} in room)", flush=True)

    try:
        conn.start()
        # Owns the socket from here on. The endpoint must not touch `ws` again.
        await conn.wait()
    finally:
        conn.kill()
        print(
            f"[{room_id}] - {conn.id} {user_id} "
            f"sent={conn.sent} dropped={conn.dropped}",
            flush=True,
        )
