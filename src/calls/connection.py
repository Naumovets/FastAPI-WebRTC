import copy

from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack, RTCIceCandidate
from aiortc.rtcrtpreceiver import RemoteStreamTrack

from calls.utils import decode_icecandidate


class Stream:
    def __init__(self):
        # self.tracks: dict[str, dict[str, List[MediaStreamTrack]]] = dict()
        self.tracks: dict[str, RemoteStreamTrack] = dict()

    def set_track(self, room: str, track: RemoteStreamTrack) -> None:
        self.tracks[room] = track

    def get_track(self, room: str) -> RemoteStreamTrack:
        if room in self.tracks.keys():
            return self.tracks[room]

    def delete_track(self, room):
        if room in self.tracks.keys():
            self.tracks.pop(room)


class WebRTCConnection:
    def __init__(self, room: str, user: str):
        self.peer: RTCPeerConnection = RTCPeerConnection()
        self.room: str = room
        self.user: str = user

    async def add_icecandidate(self, icecandidate: dict):
        """
            component: int
            foundation: str
            ip: str
            port: int
            priority: int
            protocol: str
            type: str
            relatedAddress: Optional[str] = None
            relatedPort: Optional[int] = None
            sdpMid: Optional[str] = None
            sdpMLineIndex: Optional[int] = None
            tcpType: Optional[str] = None
            """
        decoded_ice_candidate = decode_icecandidate(icecandidate)
        result_ice_candidate = RTCIceCandidate(component=decoded_ice_candidate['component'],
                                               foundation=decoded_ice_candidate['foundation'],
                                               ip=decoded_ice_candidate['ip'],
                                               port=decoded_ice_candidate['port'],
                                               priority=decoded_ice_candidate['priority'],
                                               protocol=decoded_ice_candidate['protocol'],
                                               type=decoded_ice_candidate['type'],
                                               sdpMid=decoded_ice_candidate['sdpMid'],
                                               sdpMLineIndex=decoded_ice_candidate['sdpMLineIndex']
                                               )
        # result_ice_candidate = RTCIceCandidate(*decoded_ice_candidate)
        # print(list(**decoded_ice_candidate))
        await self.peer.addIceCandidate(result_ice_candidate)


class ConsumerWebRTCConnection(WebRTCConnection):
    def __init__(self, room: str, user: str):
        super().__init__(room, user)

    async def get_answer(self, offer: dict) -> RTCSessionDescription:
        desc = RTCSessionDescription(offer['sdp'], offer['type'])
        await self.peer.setRemoteDescription(desc)
        track = copy.copy(stream.get_track(self.room))
        self.peer.addTrack(track)
        answer = await self.peer.createAnswer()
        await self.peer.setLocalDescription(answer)

        return self.peer.localDescription


class BroadcastWebRTCConnection(WebRTCConnection):
    def __init__(self, room: str, user: str):
        super().__init__(room, user)

        @self.peer.on('track')
        async def on_track(event: RemoteStreamTrack):
            print('Track received:', event.kind)
            if event.kind == "video":
                stream.set_track(room, event)

        @self.peer.on('icecandidate')
        async def on_candidate(event):
            print('Вызываю icecandidate')

    async def get_answer(self, offer: dict) -> RTCSessionDescription:
        desc = RTCSessionDescription(offer['sdp'], offer['type'])
        await self.peer.setRemoteDescription(desc)
        answer = await self.peer.createAnswer()
        await self.peer.setLocalDescription(answer)

        return self.peer.localDescription


class Room:
    def __init__(self):
        self.connections: dict[str, dict[str, WebRTCConnection]] = dict()

    def add_connection(self, room: str, user: str, connection: WebRTCConnection):
        if room not in self.connections.keys():
            self.connections[room] = {user: connection}
        else:
            self.connections[room][user] = connection

    def remove_connection(self, room: str, user: str):
        if room not in self.connections.keys():
            pass
        elif user not in self.connections[room].keys():
            pass
        else:
            self.connections[room].pop(user)


stream = Stream()
webrtc_connections = Room()
