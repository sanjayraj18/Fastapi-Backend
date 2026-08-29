from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from auth import (
    TICKET_TTL,
    TicketStore,
    can_edit,
    current_user,
    get_ticket_store,
    origin_allowed,
)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["X-User-Id"],
)


@app.post("/ws-ticket")
async def mint_ticket(
    user_id: str = Depends(current_user),
    store: TicketStore = Depends(get_ticket_store),
):
    return {"ticket": await store.mint(user_id), "expires_in": TICKET_TTL}


@app.websocket("/ws/doc/{doc_id}")
async def doc_socket(
    websocket: WebSocket,
    doc_id: str,
    ticket: str | None = None,
    store: TicketStore = Depends(get_ticket_store),
):
  
    if not origin_allowed(websocket.headers.get("origin")):
        await websocket.close(code=1008, reason="origin")
        return

    user_id = await store.redeem(ticket) if ticket else None
    if user_id is None:
        await websocket.close(code=4401, reason="bad ticket")
        return


    if not await can_edit(user_id, doc_id):
        await websocket.close(code=4403, reason="forbidden")
        return

    await websocket.accept()
    print(f"[doc {doc_id}] {user_id} joined", flush=True)

    try:
        while True:
            msg = await websocket.receive_text()
            await websocket.send_text(f"{user_id}: {msg}")
    except WebSocketDisconnect:
        print(f"[doc {doc_id}] {user_id} left", flush=True)
