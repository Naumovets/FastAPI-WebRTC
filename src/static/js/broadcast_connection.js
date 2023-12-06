class Connection{
    constructor(chatSocket, stream){
        this.chatSocket = chatSocket;
        this.PeerConnection = new RTCPeerConnection();
        this.stream = stream;
        this.videoTrack = stream.getVideoTracks()[0];
        const localVideo = document.getElementById('myVideo')
        localVideo.srcObject = stream; 
        this.PeerConnection.addTrack(this.videoTrack, this.stream);

        this.PeerConnection.addEventListener('track', (event)=>{
            const videoDiv = document.getElementById('video');
            videoDiv.srcObject = event.streams[0];
        });
    }

    async sendOffer(){
        const offer = await this.PeerConnection.createOffer()
        await this.PeerConnection.setLocalDescription(offer);
        this.chatSocket.send(JSON.stringify({
            'type': 'offer',
            'data': this.PeerConnection.localDescription,
            'details': null
        }));

        this.PeerConnection.addEventListener('icecandidate', (event)=>{
            if(event.candidate && event.candidate.candidate){
                this.chatSocket.send(JSON.stringify({
                    'type': 'icecandidate',
                    'data': event.candidate,
                    'details': null
                }))
//                alert('Вызывается icecandidate');
            }
        });
    }

    async setAnswer(answer){
        await this.PeerConnection.setRemoteDescription(answer);
        alert('Соединение произошло')
    }

    async setIceCandidate(icecandidate){
        await this.PeerConnection.addIceCandidate(new RTCIceCandidate(icecandidate));
    }
}