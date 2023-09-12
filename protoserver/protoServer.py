from __future__ import annotations
from typing import TYPE_CHECKING

from protoserver.config import Config
from protoserver.http.client import Client

if TYPE_CHECKING:
    from protoserver.servers.iServer import IConnection


class ProtoServer(object):

    def __init__(self, config: None | Config = None) -> None:
        if config is None: config = Config.loadFromFile()
        self.config = config

        self.handler = self.config.getHandler()(self.config)
        self.server = self.config.getServer()(self.config)

        self.isRunning = False
        self.connections: list[IConnection] = []

    def run(self) -> None:

        self.isRunning = True
        while self.isRunning:
            connection = self.server.accept()
            if connection is None:
                break
            client = Client(self.config, connection, self.handler)

        self.stop()

    def stop(self) -> None:
        self.server.stop()