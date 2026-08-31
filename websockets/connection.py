from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import contextlib
import json


class Connection:
    def __init__(self, id: str, ws: WebSocket, room_id: str, user_id: str):
        self.id = id
        self.user_id = user_id
        self.room_id = room_id
        self.ws = ws
        self.out = asyncio.Queue(maxsize=256)

        self.room = None              # set by registry.join() — the reader uses this

        self.sent = 0
        self.dropped = 0
        self.close_code = 1000
        self.close_reason = ""

        self._closing = False
        self._writer_task: asyncio.Task | None = None
        self._reader_task: asyncio.Task | None = None
        self._close_task: asyncio.Task | None = None

    def start(self):
        self._writer_task = asyncio.create_task(self._writer_loop())
        self._reader_task = asyncio.create_task(self._reader_loop())

    async def wait(self):
        """Block until this connection is finished.

        Exists so the endpoint never has to touch _reader_task directly.
        """
        if self._reader_task is not None:
            with contextlib.suppress(asyncio.CancelledError):
                await self._reader_task

    async def _reader_loop(self):
        """The ONLY task that calls ws.receive()."""
        try:
            while True:
                raw = await self.ws.receive_text()
                msg = json.loads(raw)
                
                #presence logic
                if msg["type"] == "edit":
                    if self.room:
                        self.room.enqueue(msg["data"])

                elif msg["type"] == "cursor":
                    if self.room:
                        self.room.update_presence(
                            self.user_id, msg["x"], msg["y"]
                        )

        except WebSocketDisconnect:
            pass
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"[{self.id}] reader error: {e!r}", flush=True)
        finally:
            self.kill()

    async def _writer_loop(self):
        """The ONLY task that calls ws.send()."""
        try:
            while True:
                msg = await self.out.get()
                await self.ws.send_text(msg)
                self.sent += 1
        except asyncio.CancelledError:
            # kill() cancelled us. Let it propagate -- swallowing cancellation
            # is how tasks become unkillable.
            raise
        except (WebSocketDisconnect, RuntimeError):
            self.kill()
        except Exception as e:
            print(f"[{self.id}] writer error: {e!r}", flush=True)
            self.kill()

    def enqueue(self, msg: str, *, droppable: bool = False) -> bool:
        """Sync. Never blocks. False means the message did not land."""
        if self._closing:
            return False
        try:
            self.out.put_nowait(msg)
            return True
        except asyncio.QueueFull:
            if droppable:
                # Stale by definition -- a newer message supersedes this one.
                self.dropped += 1
                return False
            # A document op. Dropping it would desync this client forever and
            # it would never know. Force a reconnect + resync instead.
            self.kill(4008, "resync")
            return False

    def kill(self, code: int = 1000, reason: str = ""):
        """Shut down THIS connection only: cancel its tasks, close its socket.

        Room membership and teardown are the registry's job (registry.leave),
        so kill() no longer touches rooms -- otherwise instant removal here
        would defeat the registry's 30s grace period.
        """
        if self._closing:
            return
        self._closing = True
        self.close_code, self.close_reason = code, reason

        # Never cancel the task we are currently running on. kill() is normally
        # called from _reader_loop's finally, and cancelling yourself there
        # makes `await self._reader_task` raise CancelledError into the endpoint.
        current = asyncio.current_task()
        for task in (self._writer_task, self._reader_task):
            if task is not None and task is not current:
                task.cancel()

        # Keep a reference: asyncio holds only weak refs to tasks, so a
        # fire-and-forget create_task() can be garbage collected mid-flight.
        self._close_task = asyncio.create_task(self._close())

    async def _close(self):
        try:
            await self.ws.close(code=self.close_code, reason=self.close_reason)
        except Exception:
            pass

    def __repr__(self):
        return (
            f"<Conn {self.id} {self.user_id} q={self.out.qsize()}"
            f" sent={self.sent} dropped={self.dropped}>"
        )