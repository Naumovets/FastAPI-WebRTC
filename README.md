# FastAPI-WebRTC
[![Typing SVG](https://readme-typing-svg.herokuapp.com?color=%15192b&lines=Python+WebRTC+SFU+and+signal+server)](https://git.io/typing-svg)  
This project about realization WebRTC SFU and signal server with python.

## About project
### Signal server and mesh architechture
Signal server is needed for sharing data for peer to peer (p2p) connection between clients. We can use it for develop group conference  (p2p connection with everyone in the room).
This architecture's called mesh.

Pros of mesh:
- easy and fast realization
- low load server
Cons of mesh:
- hight load client with growth count client in the room
- impossible record conference

### SFU server
SFU server is needed for optimization load for client in group conference.  
It's done with the help intermediate server is called SFU (Selective Forwarding Unit) server.
#### how it work
SFU server use p2p connect with every member of room, get media tracks and send this tracks to other members of room.  
It help client send only 1 media track to server instead of sending N-1 sames media tracks to N-1 members of room  
(N-1 because 1 of N members of room is you).
#### кайфовый bonus
Also this architecture give us opportunity to filter of media tracks  
for example, if you are speaker and in the room many listeners, who don't say, we can just give everyone only tracks of speaker without tracks of listeners.

pros of SFU server:
- less load client than mesh
- not hight load server
- opportunity filters media tracks
- can recond conference
  
cons of SFU server:
- more load server than mesh
- also can hight load client

## Useful materials:
- [samples WebRTC](https://webrtc.org/?)
- [aiortc](https://aiortc.readthedocs.io/en/latest/index.html)
- [FastAPI](https://fastapi.tiangolo.com/)

## Start project

- install python 3.10.11 from [official website](https://www.python.org/)
- run command line
- create and up virtual environments:
  ```
  python -m venv venv
  ```
  ```
  .\venv\Scripts\activate
  ```
- install dependencies:
  ```
  pip install -r requirements.txt
  ```
- open sourse project folder
  ```
  cd src
  ```
- start uvicorn server:

  ```
  uvicorn main:app --reload --log-level=info
  ```
  Flag '--reload' is needed for reload server every time with edit, etc.  
  Flag '--log-level=info' is needed for showing info in command line about working of uvicorn server.

## Docs of project:
Just open /docs :D
