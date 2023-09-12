from __future__ import annotations
from typing import TYPE_CHECKING

from protoserver.config import Config
from protoserver.handlers.iHandler import IHandler
from protoserver.http.response import Response

if TYPE_CHECKING:
    from protoserver.http.request import Request
    from protoserver.http.statusCodes import StatusCode


class MirrorHandler(IHandler):

    def handleRequest(self, request: Request) -> Response | None:
        response = Response()

        response.setBody(request.raw.decode("iso-8859-1"))

        return response
    
    def handleError(self, statusCode: StatusCode) -> Response | None:
        return super().handleError(statusCode)
    
Config.registerHandler("MirrorHandler", MirrorHandler)