
from connection import Connection
import asyncio
import time
import json

class Room:
    def __init__(self,id : str):
        self.id = id
        self.seq = 0  
        self.state = ""
        self.conns: dict[str,Connection] = {}
        self.inbox = asyncio.Queue(maxsize=256)
        self.presence : dict[str, dict] = {}

    def start(self):
        self.consumer = asyncio.create_task(self._consume())
        self.sweeper = asyncio.create_task(self._presence_sweeper())

    def enqueue(self,msg : str) -> bool:
        try:
            self.inbox.put_nowait(msg)
            return True
        except asyncio.QueueFull:
            return False

    async def _consume(self):
        while True:
            msg = await self.inbox.get()
            self.seq += 1
            self.state += msg
            payload = f"[{self.seq}] {msg}"
            for conn in list(self.conns.values()):
                conn.enqueue(payload) 

    def update_presence(self, user_id : str, x: int, y : int):
        now = time.monotonic()
        entry = self.presence.get(user_id)

        if entry and now - entry["ts"] < 0.05:
            return
        

        self.presence[user_id] = {"x": x, "y": y , "ts": now}

        payload = json.dumps({"type" : "cursor", "user" : user_id , "x" : x,"y" : y})

        for conn in list(self.conns.values()):
            conn.enqueue(payload, droppable=True)
    

    async def _presence_sweeper(self):
        while True:
            await asyncio.sleep(5)
            now = time.monotonic()
            stale = [
                    uid for uid, e in self.presence.items()
                    if now - e["ts"] > 15          
            ]

            for uid in stale:
                del self.presence[uid]
                payload = json.dumps({"type": "cursor_leave", "user": uid})
                for conn in list(self.conns.values()):
                    conn.enqueue(payload, droppable=True)