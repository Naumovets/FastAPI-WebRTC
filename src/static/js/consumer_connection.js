class Connection{
    constructor(chatSocket){
        this.chatSocket = chatSocket;
        this.PeerConnection = new RTCPeerConnection();
        this.PeerConnection.addEventListener('track', (event)=>{
            console.log(event.streams[0])
            const videoDiv = document.getElementById('video');
            videoDiv.srcObject = event.streams[0];
        });
        this.PeerConnection.addTransceiver('video', {'direction': 'recvonly'})
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