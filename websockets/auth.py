import os
import time
import asyncio
import secrets
from typing import Protocol
from fastapi import HTTPException, Header

ALLOWED_ORIGINS = frozenset(
    o.strip()
    for o in os.environ.get(
        "WS_ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:8000"
    ).split(",")

    if o.strip() 
)

def origin_allowed(origin: str | None) -> bool:
    if origin is None:
        return True
    return origin in ALLOWED_ORIGINS

TICKET_TTL = int(os.environ.get("WS_TICKET_TTL", 30))



class TicketStore(Protocol):
    async def mint(self, user_id: str) -> str : ...
    async def redeem(self, ticket : str) -> str | None : ...



class MemoryTicketStore:
    def __init__(self) -> None:
        self._tickets: dict[str, tuple[str, float]] = {}
        self._lock = asyncio.Lock()

    async def mint(self,user_id : str) -> str:
        ticket = secrets.token_urlsafe(32)
        async with self._lock:
            self._tickets[ticket] = (user_id, time.monotonic() + TICKET_TTL)
        return ticket

    async def redeem(self, ticket : str) -> str | None:
        async with self._lock:
            entry = self._tickets.pop(ticket, None)
        if entry is None:
            return None
        user_id, expires_at = entry
        return None if time.monotonic() > expires_at else user_id



class RedisTicketStore:
    def __init__(self, redis) -> None:
        self._r = redis

    async def mint(self, user_id :str) -> str:
        ticket = secrets.token_urlsafe(32)
        await self._r.set(f"wst:{ticket}", user_id, ex=TICKET_TTL, nx=True)
        return ticket

    async def redeem(self, ticket : str) -> str | None:
        value = await self._r.getdel(f"wst:{ticket}")
        if value is None:
            return None
        return value.decode() if isinstance(value, bytes) else value

_store : TicketStore| None = None



def get_ticket_store() -> TicketStore:
    global _store
    if _store is None:
        url = os.environ.get("REDIS_URL")
        if url:
            import redis.asyncio as aioredis

            _store = RedisTicketStore(aioredis.from_url(url))

        else:
            _store = MemoryTicketStore()
    return _store



def current_user(x_user_id: str | None = Header(default=None)) -> str:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="not authenticated")
    return x_user_id


DOC_OWNERS = {"doc-a": "alice", "doc-b": "bob"}


async def can_edit(user_id: str, doc_id: str) -> bool:
    return DOC_OWNERS.get(doc_id) == user_id
