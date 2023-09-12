from queue import Queue
from socket import socket
from threading import Thread
from unittest import TestCase

from protoserver.config import Config
from protoserver.handlers import MirrorHandler
from protoserver.http.request import Request


class testMirrorHandler(TestCase):

    def testMirrorHandler(self) -> None:
        config = Config.getMinimalValidConfig({"HANDLER": "MirrorHandler"})
        handler = MirrorHandler(config)

        requestBytes = [
            b"GET / HTTP/1.1\r\n\r\n",
            b"GET /path/to/resource?query=value\r\nHost: localhost\r\nX-Custom-Header: value\r\n\r\nBody Text",
        ]

        for test in requestBytes:
            with self.subTest():
                request = Request(test)
                response = handler.handleRequest(request)

                if response is None:
                    self.fail("Response was None.")

                expectedResponse = f"HTTP/1.1 200 OK\r\nContent-Length: {len(test)}\r\n\r\n{test.decode('iso-8859-1')}".encode("iso-8859-1")

                self.assertEqual(expectedResponse, response.build())
