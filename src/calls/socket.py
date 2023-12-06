from starlette.types import Scope, Receive, Send
from fastapi import WebSocket
import json
from abc import ABC, abstractmethod
from typing import List


class Socket(WebSocket):
    def __init__(self, name: None | str, scope: Scope, receive: Receive, send: Send):
        super().__init__(scope, receive, send)
        self.name = name


class ConnectionManager(ABC):
    def __init__(self):
        self.room_connections: dict[str, dict[str, Socket]] = dict()

    @abstractmethod
    async def connect(self, websocket: Socket, room: str):
        ...

    @abstractmethod
    async def disconnect(self, websocket: Socket, room: str) -> None:
        ...

    async def send_personal_message(self, message: str, websocket: Socket) -> None:
        await websocket.send_text(message)

    async def broadcast(self, room: str, message: str) -> None:
        if room in self.room_connections.keys():
            for socket in self.room_connections[room].keys():
                await self.room_connections[room][socket].send_text(message)


class P2PConnectionManager(ConnectionManager):
    def __init__(self):
        super().__init__()

    async def connect(self, websocket: Socket, room: str) -> bool:
        await websocket.accept()
        if room not in self.room_connections.keys():
            websocket.name = 'user_1'
            self.room_connections[room] = {websocket.name: websocket}
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
                self.room_connections[room][websocket.name] = websocket
                socket_name = list(self.room_connections[room].keys())[0]
                socket = self.room_connections[room][socket_name]
                if len(self.room_connections[room]) == 2:
                    data = json.dumps({
                        'type': 'status',
                        'data': 'connected',
                        'details': None
                    })
                    await self.send_personal_message(message=data, websocket=socket)
        return True

    async def disconnect(self, websocket: Socket, room: str):
        try:
            self.room_connections[room].pop(websocket.name)
            if len(self.room_connections[room]) == 1:
                socket_name = list(self.room_connections[room].keys())[0]
                socket = self.room_connections[room][socket_name]
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
        except Exception as e:
            print(e)


class GroupConnectionManager(ConnectionManager):
    async def connect(self, websocket: Socket, room: str) -> str:
        await websocket.accept()
        if room not in self.room_connections.keys():
            websocket.name = 'user_1'
            self.room_connections[room] = {websocket.name: websocket}
        else:
            websocket.name = f'user_{len(self.room_connections[room]) + 1}'
            self.room_connections[room][websocket.name] = websocket
        data = json.dumps({
            'type': 'status',
            'data': 'connected',
            'detail': None
        })
        await self.send_personal_message(message=data, websocket=websocket)
        return websocket.name

    async def disconnect(self, websocket: Socket, room: str):
        try:
            self.room_connections[room].pop(websocket.name)
            if len(self.room_connections[room]) == 0:
                self.room_connections.pop(room)
        except KeyError:
            print('The room does not exist')
