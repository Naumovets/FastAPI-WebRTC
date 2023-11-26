import json
from fastapi import APIRouter
from fastapi.websockets import WebSocketDisconnect

from calls.connection import P2PConnectionManager, GroupConnectionManager
from calls.socket import Socket

router = APIRouter(prefix='/calls', tags=['Calls'])


p2p_manager = P2PConnectionManager()
group_manager = GroupConnectionManager()


@router.websocket('/ws/p2p/{room}')
async def websocket_p2p_room(websocket: Socket, room: str):
    result = await p2p_manager.connect(websocket, room)
    if result:
        try:
            while True:
                data = json.loads(await websocket.receive_text())
                if data['type'] == 'message':
                    result_data = json.dumps({
                        'type': 'message',
                        'data': f"{websocket.name}: {data['data']}",
                        'details': None
                    })
                    await p2p_manager.broadcast(room=room, message=result_data)
                elif data['type'] in ['offer', 'answer', 'icecandidate']:
                    if p2p_manager.room_connections[room][0] != websocket:
                        other_socket = p2p_manager.room_connections[room][0]
                    else:
                        other_socket = p2p_manager.room_connections[room][1]
                    await p2p_manager.send_personal_message(message=json.dumps(data), websocket=other_socket)
        except WebSocketDisconnect:
            await p2p_manager.disconnect(websocket, room)


@router.websocket('/ws/group/{room}')
async def websocket_group_room(websocket: Socket, room: str):
    ...
