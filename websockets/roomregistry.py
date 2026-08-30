from room import Room
from connection import Connection
import asyncio

class RoomRegistry:
    def __init__(self):
        self.rooms : dict[str, Room] = {}

    def get_or_create_room(self, room_id : str) -> Room:
        if room_id not in self.rooms:
            room = Room(room_id)
            room.start()
            self.rooms[room_id] = room
        return self.rooms[room_id]
       
    def join(self, room_id: str, conn: Connection) -> Room:
        room = self.get_or_create_room(room_id)   
        room.conns[conn.user_id] = conn          
        return room

    def leave(self, room_id: str, user_id: str):
        room = self.rooms.get(room_id)
        if not room:
            return
        room.conns.pop(user_id, None)             
        if len(room.conns) == 0:                  
            self._schedule_teardown(room_id) 

    def _schedule_teardown(self, room_id : str):
        async def _teardown():
            await asyncio.sleep(30)   
            room = self.rooms.get(room_id)

            if room and len(room.conns) == 0:
                self._snapshot(room.state)
                if room.consumer:
                    room.consumer.cancel()
                del self.rooms[room_id]

        asyncio.create_task(_teardown())

    def _snapshot(self, state):
        # save to DB/file — stub for now
        print(f"snapshot saved: {state!r}")