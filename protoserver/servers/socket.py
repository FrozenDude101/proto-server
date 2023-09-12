from __future__ import annotations
from socket import create_server, socket

from protoserver.config import Config
from protoserver.servers.iServer import IConnection, IServer


class SocketConnection(IConnection):

    def __init__(self, config: Config, server: SocketServer, connection: socket, clientName: str, port: int) -> None:
        super().__init__(config, server)

        self.connection = connection
        self.clientName = clientName
        self.port = port

    def recv(self) -> bytes:
        return self.connection.recv(8192)
    
    def send(self, data: bytes) -> None:
        self.connection.sendall(data)
    
    def close(self) -> None:
        super().close()
        self.connection.close()


class SocketServer(IServer):

    def __init__(self, config: Config) -> None:
        super().__init__(config)

        self.hostname = config.get("HOSTNAME")
        self.port = config.get("PORT", int)

        self.server = socket()

        try:
            self.server.bind((self.hostname, self.port))
        except:
            self.server.close()
            raise
        
        self.server.listen()

    def accept(self) -> None | SocketConnection:
        try:
            connection, address = self.server.accept()
        except OSError:
            return None
        conn = SocketConnection(self.config, self, connection, address[0], address[1])
        self.connections.append(conn)
        return conn
    
    def stop(self) -> None:
        super().stop()
        self.server.close()
        
Config.registerServer("SocketServer", SocketServer)