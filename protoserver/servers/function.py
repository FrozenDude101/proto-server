from __future__ import annotations
from queue import Queue

from protoserver.config import Config
from protoserver.servers.iServer import IConnection, IServer


class FunctionConnection(IConnection):

    requestBuffer = Queue()
    responseBuffer = Queue()

    def recv(self) -> bytes:
        return self.requestBuffer.get()
    
    def send(self, data: bytes) -> None:
        self.responseBuffer.put(data)
    
    def stop(self) -> None:
        return
    
    def clientSend(self, data: bytes) -> None:
        self.requestBuffer.put(data)

    def clientRecv(self) -> bytes:
        return self.responseBuffer.get()


class FunctionServer(IServer):

    def __init__(self, *args) -> None:
        super().__init__(*args)

        self.connection = None

    def accept(self) -> None | FunctionConnection:
        if self.connection is not None:
            return None

        self.connection = FunctionConnection(self.config, self)
        self.connections.append(self.connection)
        return self.connection
    
    def getConnection(self) -> FunctionConnection:
        while self.connection is None:
            pass
        return self.connection
        
Config.registerServer("FunctionServer", FunctionServer)