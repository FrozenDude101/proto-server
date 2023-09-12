from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protoserver.config import Config


class IConnection(ABC):

    def __init__(self, config: Config, server: IServer) -> None:
        self.config = config
        self.server = server
    
    @abstractmethod
    def recv(self) -> bytes:
        raise NotImplementedError()

    @abstractmethod
    def send(self, data: bytes) -> None:
        raise NotImplementedError()
    
    def close(self) -> None:
        self.server.onConnectionClose(self)
    

class IServer(ABC):

    def __init__(self, config: Config) -> None:
        self.config = config
        self.connections: list[IConnection] = []

    @abstractmethod
    def accept(self) -> None | IConnection:
        raise NotImplementedError()
    
    def stop(self) -> None:
        for connection in self.connections.copy():
            connection.close()
    
    def onConnectionClose(self, connection: IConnection) -> None:
        self.connections.remove(connection)
