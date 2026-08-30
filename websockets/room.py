
from connection import Connection
import asyncio

class Room:
    def __init__(self,id : str):
        self.id = id
        self.seq = 0  
        self.state = ""
        self.conns: dict[str,Connection] = {}
        self.inbox = asyncio.Queue(maxsize=256)

    def start(self):
        self.consumer = asyncio.create_task(self._consume())

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

