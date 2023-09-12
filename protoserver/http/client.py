from __future__ import annotations
from threading import Thread
from typing import TYPE_CHECKING

from protoserver.http.request import Request
from protoserver.http.response import Response
from protoserver.http.statusCodes import StatusCode

if TYPE_CHECKING:
    from protoserver import Config
    from protoserver.handlers import IHandler
    from protoserver.servers import IConnection


class Client(object):
    
    def __init__(self, config: Config, connection: IConnection, handler: IHandler) -> None:
        self.config = config
        self.connection = connection
        self.handler = handler

        self.isRunning = True
        self.thread = Thread(target = self.loop)
        self.thread.start()

    def loop(self) -> None:

        while self.isRunning:
            request = self.recv()
            if request is None:
                continue

            response = self.handler.handleRequest(request)
            if response is None:
                continue

            self.send(response)

        self.close()

    def recv(self) -> None | Request:
        requestBytes = self.connection.recv()
        if requestBytes == b"":
            self.isRunning = False
            return None
        
        request = Request(requestBytes)

        match (request.status):
            case "OK":
                return request
            case "BAD_REQUEST":
                response = self.handler.handleError(StatusCode.BAD_REQUEST)
                if response is not None:
                    self.send(response)
                return None

    def send(self, response: Response) -> None:
        self.connection.send(response.build())

    def close(self) -> None:
        self.connection.close()

