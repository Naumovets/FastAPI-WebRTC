import json
from fastapi import APIRouter
from fastapi.websockets import WebSocketDisconnect

from calls.connection import BroadcastWebRTCConnection, ConsumerWebRTCConnection, webrtc_connections
from calls.socket import Socket, P2PConnectionManager, GroupConnectionManager

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
                    socket_names = list(p2p_manager.room_connections[room].keys())
                    if p2p_manager.room_connections[room][socket_names[0]] != websocket:
                        other_socket = p2p_manager.room_connections[room][socket_names[0]]
                    else:
                        other_socket = p2p_manager.room_connections[room][socket_names[1]]
                    await p2p_manager.send_personal_message(message=json.dumps(data), websocket=other_socket)
        except WebSocketDisconnect:
            await p2p_manager.disconnect(websocket, room)


@router.websocket('/ws/broadcast/{room}')
async def websocket_group_room(websocket: Socket, room: str):
    user = await group_manager.connect(websocket, room)

    try:
        while True:
            data = json.loads(await websocket.receive_text())
            if data['type'] == 'message':
                result_data = json.dumps({
                    'type': 'message',
                    'data': f"{websocket.name}: {data['data']}",
                    'details': None
                })
                await group_manager.broadcast(room=room, message=result_data)
            elif data['type'] == 'offer':
                broadcast = BroadcastWebRTCConnection(room, user)
                answer = await broadcast.get_answer(data['data'])
                result_data = {
                    'type': 'answer',
                    'data': {'sdp': answer.sdp, 'type': answer.type},
                    'details': None
                }
                webrtc_connections.add_connection(room, user, broadcast)
                await group_manager.send_personal_message(json.dumps(result_data), websocket)
            elif data['type'] == 'icecandidate':
                broadcast = webrtc_connections.connections[room][user]
                await broadcast.add_icecandidate(data['data'])

    except WebSocketDisconnect:
        await group_manager.disconnect(websocket, room)
        webrtc_connections.remove_connection(room, user)


@router.websocket('/ws/consumer/{room}')
async def websocket_group_room_consumer(websocket: Socket, room: str):
    user = await group_manager.connect(websocket, room)

    try:
        while True:
            data = json.loads(await websocket.receive_text())
            if data['type'] == 'message':
                result_data = json.dumps({
                    'type': 'message',
                    'data': f"{websocket.name}: {data['data']}",
                    'details': None
                })
                await group_manager.broadcast(room=room, message=result_data)
            elif data['type'] == 'offer':
                consumer = ConsumerWebRTCConnection(room, user)
                answer = await consumer.get_answer(data['data'])
                result_data = {
                    'type': 'answer',
                    'data': {'sdp': answer.sdp, 'type': answer.type},
                    'details': None
                }
                webrtc_connections.add_connection(room, user, consumer)
                await group_manager.send_personal_message(json.dumps(result_data), websocket)
            elif data['type'] == 'icecandidate':
                consumer = webrtc_connections.connections[room][user]
                await consumer.add_icecandidate(data['data'])

    except WebSocketDisconnect:
        await group_manager.disconnect(websocket, room)
        webrtc_connections.remove_connection(room, user)
