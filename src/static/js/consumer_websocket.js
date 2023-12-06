async function start(){
    const room = document.getElementById('room').value;
    var ws = new WebSocket(`ws://localhost:8000/calls/ws/consumer/${room}`);
    var connection = new Connection(ws);

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if(data.type == 'status'){
            if (data.data == 'connected'){
                connection.sendOffer();
            }
        }
        else if(data.type == 'answer'){
            connection.setAnswer(data.data);
        }
        else if(data.type == 'icecandidate'){
            connection.setIceCandidate(data.data);
        }
        else if(data.type == 'message'){
            var messages = document.getElementById('messages')
            var message = document.createElement('li')
            var content = document.createTextNode(data.data)
            message.appendChild(content)
            messages.appendChild(message)
        }
        else if(data.type == 'error'){
            var messages = document.getElementById('messages')
            var message = document.createElement('div')
            message.className = 'alert alert-danger'
            var content = document.createTextNode(data.details)
            message.appendChild(content)
            messages.appendChild(message)
        }
    }

    document.querySelector('#chatForm').onsubmit = function(event) {
            var input = document.getElementById("messageText");
            data = JSON.stringify({
                'type': 'message',
                'data': input.value,
                'details': null
            })
            ws.send(data);
            input.value = ''
            event.preventDefault()
        };

}

document.addEventListener('DOMContentLoaded', async function() {
  await start();
});