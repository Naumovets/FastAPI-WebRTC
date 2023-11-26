from starlette.types import Scope, Receive, Send
from fastapi import WebSocket


class Socket(WebSocket):
    def __init__(self, name: None | str, scope: Scope, receive: Receive, send: Send):
        super().__init__(scope, receive, send)
        self.name = name
