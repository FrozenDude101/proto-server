from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protoserver import Config
    from protoserver.http import Request, Response, StatusCode


class IHandler(ABC):

    def __init__(self, config: Config) -> None:
        self.config = config

    @abstractmethod
    def handleRequest(self, request: Request) -> None | Response:
        raise NotImplementedError()
    
    @abstractmethod
    def handleError(self, statusCode: StatusCode) -> None | Response:
        raise NotImplementedError()