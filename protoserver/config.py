from __future__ import annotations
import dotenv
from typing import Mapping, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from protoserver.handlers.iHandler import IHandler
    from protoserver.servers.iServer import IServer


_T = TypeVar("_T")

class Config(object):

    MINIMAL_VALID_CONFIG_OPTIONS = {
        "HANDLER": "MirrorHandler",
        "SERVER":  "FunctionServer",
    }

    _registeredHandlers: dict[str, type[IHandler]] = {}
    _registeredServers: dict[str, type[IServer]] = {}

    def __init__(self, data: Mapping[str, None | str]) -> None:
        self._config = data

        possibleHandlers = self._registeredHandlers.keys()
        if self._config["HANDLER"] not in possibleHandlers:
            raise ValueError(f"HANDLER not correctly set in .env.\nMust be one of:\n\t{', '.join(possibleHandlers)}")

        possibleServers = self._registeredServers.keys()
        if self._config["SERVER"] not in possibleServers:
            raise ValueError(f"SERVER not correctly set in .env.\nMust be one of:\n\t{', '.join(possibleServers)}")
        
    @classmethod
    def loadFromFile(cls, path = ".env") -> Config:
        return Config(dotenv.dotenv_values(path))
    
    @classmethod
    def getMinimalValidConfig(cls, data: None | Mapping[str, None | str] = None) -> Config:
        if data is None: data = {}
        return Config(Config.MINIMAL_VALID_CONFIG_OPTIONS | data)


    def get(self, key: str, type: type[_T] = str) -> _T:
        if key not in self._config:
            raise KeyError(f"Unknown config option {key}.\nMaybe it wasn't in .exampleEnv?")
        
        value = self._config[key]
        if value is None:
            raise ValueError(f"{key} has no default value, and wasn't set in .env.")
        
        return type(value)
    
    def getHandler(self) -> type[IHandler]:
        handler = self.get("HANDLER")
        return self._registeredHandlers[handler]
    
    def getServer(self) -> type[IServer]:
        server = self.get("SERVER")
        return self._registeredServers[server]
    
    @classmethod
    def registerHandler(cls, name: str, handler: type[IHandler]) -> None:
        cls._registeredHandlers[name] = handler
    
    @classmethod
    def registerServer(cls, name: str, server: type[IServer]) -> None:
        cls._registeredServers[name] = server