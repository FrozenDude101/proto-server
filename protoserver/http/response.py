from __future__ import annotations
from typing import Self

from protoserver.http.statusCodes import StatusCode


class Response(object):

    def __init__(self) -> None:

        self.statusCode = StatusCode.OK
        self.headers = {}
        self.body = ""

    def setStatusCode(self, statusCode: StatusCode) -> Self:
        self.statusCode = statusCode
        return self
    
    def setHeader(self, header: str, value: str) -> Self:
        self.headers[header] = value
        return self
    
    def setBody(self, body: str) -> Self:
        self.body = body

        bodyLength = len(self._buildBody())
        self.setHeader("Content-Length", str(bodyLength))

        return self

    def build(self) -> bytes:
        return b"".join([
            self._buildStatusLine(),
            self._buildHeaders(),
            self._buildBody(),            
        ])

    def _buildStatusLine(self) -> bytes:
        statusLine = f"HTTP/1.1 {self.statusCode.value} {self.statusCode.name}\r\n"
        return statusLine.encode("iso-8859-1")

    def _buildHeaders(self) -> bytes:
        headerString = ""
        for name, value in self.headers.items():
            headerString += f"{name}: {value}\r\n"

        headerString += "\r\n"
        return headerString.encode("iso-8859-1")

    def _buildBody(self) -> bytes:
        return self.body.encode("iso-8859-1")