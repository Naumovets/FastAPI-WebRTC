import json
from abc import ABC, abstractmethod
from typing import List
from calls.socket import Socket


class ConnectionManager(ABC):
    def __init__(self):
        self.room_connections: dict[str, List[Socket]] = dict()

    @abstractmethod
    async def connect(self, websocket: Socket, room: str) -> bool:
        ...

    @abstractmethod
    async def disconnect(self, websocket: Socket, room: str) -> None:
        ...

    async def send_personal_message(self, message: str, websocket: Socket) -> None:
        await websocket.send_text(message)

    async def broadcast(self, room: str, message: str) -> None:
        if room in self.room_connections.keys():
            for connection in self.room_connections[room]:
                await connection.send_text(message)


class P2PConnectionManager(ConnectionManager):
    def __init__(self):
        super().__init__()

    async def connect(self, websocket: Socket, room: str):
        await websocket.accept()
        if room not in self.room_connections.keys():
            websocket.name = 'user_1'
            self.room_connections[room] = [websocket]
        else:
            if len(self.room_connections[room]) == 2:
                data = json.dumps({
                    'type': 'error',
                    'data': None,
                    'details': 'Not allowed more than 2 users'
                })
                await self.send_personal_message(message=data, websocket=websocket)
                await websocket.close()
                return False
            else:
                websocket.name = f'user_{len(self.room_connections[room]) + 1}'
                self.room_connections[room].append(websocket)
                if len(self.room_connections[room]) == 2:
                    socket = self.room_connections[room][0]
                    data = json.dumps({
                        'type': 'status',
                        'data': 'connected',
                        'details': None
                    })
                    await self.send_personal_message(message=data, websocket=socket)
                else:
                    socket = self.room_connections[room][0]
                    data = json.dumps({
                        'type': 'status',
                        'data': None,
                        'details': 'You are alone in the room'
                    })
                    await self.send_personal_message(message=data, websocket=socket)
        return True

    async def disconnect(self, websocket: Socket, room: str):
        try:
            self.room_connections[room].remove(websocket)
            if len(self.room_connections[room]) == 1:
                socket = self.room_connections[room][0]
                data = json.dumps({
                    'type': 'status',
                    'data': 'disconnected',
                    'details': None
                })
                await self.send_personal_message(message=data, websocket=socket)
            else:
                self.room_connections.pop(room)
        except KeyError:
            data = json.dumps({
                'type': 'error',
                'data': None,
                'details': 'The room does not exist'
            })
            await self.send_personal_message(message=data, websocket=websocket)


class GroupConnectionManager(ConnectionManager):
    async def connect(self, websocket: Socket, room: str) -> bool:
        ...

    async def disconnect(self, websocket: Socket, room: str) -> None:
        ...
