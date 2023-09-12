from unittest import TestCase

from protoserver.http.response import Response
from protoserver.http.statusCodes import StatusCode


class testFunctionServer(TestCase):

    def testMinimalRequest(self) -> None:
        response = Response()\
            .build()

        self.assertEqual(b"HTTP/1.1 200 OK\r\n\r\n", response)

    def testStatusCodes(self) -> None:
        for code in StatusCode:
            with self.subTest():
                response = Response()\
                    .setStatusCode(code)\
                    .build()

                expectedResponse = f"HTTP/1.1 {code.value} {code.name}\r\n\r\n".encode("iso-8859-1")
                self.assertEqual(expectedResponse, response)

    def testSetSingleHeader(self) -> None:
        response = Response()\
            .setHeader("X-Custom-Header", "Value")\
            .build()

        expectedResponse = b"HTTP/1.1 200 OK\r\nX-Custom-Header: Value\r\n\r\n"
        self.assertEqual(expectedResponse, response)

    def testSetMultipleHeader(self) -> None:
        response = Response()\
            .setHeader("X-Custom-Header", "Value")\
            .setHeader("X-Custom-Header2", "Value2")\
            .build()

        expectedResponse = b"HTTP/1.1 200 OK\r\nX-Custom-Header: Value\r\nX-Custom-Header2: Value2\r\n\r\n"
        self.assertEqual(expectedResponse, response)

    def testSetBody(self) -> None:
        response = Response()\
            .setBody("Body Text")\
            .build()
        
        expectedResponse = b"HTTP/1.1 200 OK\r\nContent-Length: 9\r\n\r\nBody Text"
        self.assertEqual(expectedResponse, response)