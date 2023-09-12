from unittest import TestCase

from protoserver.http.request import Request

class testFunctionServer(TestCase):

    def assertRequestEquals(self, request: Request, method: str, path: str, queries: dict, version: str, headers: dict, body: str):
        self.assertEqual(request.method, method)
        self.assertEqual(request.path, path)
        self.assertDictEqual(request.queries, queries)
        self.assertEqual(request.version, version)
        self.assertDictEqual(request.headers, headers)
        self.assertEqual(request.body, body)
        self.assertEqual(request.status, "OK")


    def testBadRequests(self) -> None:
        requestBytes = [
            b"",
            b"/index.html",
            b"GET /index.html HTTP/1.1\r\nHost: localhost",
            b"GET /index.html HTTP/1.1\r\nHost: localhost\r\n",
        ]

        for rBytes in requestBytes:
            with self.subTest():
                request = Request(rBytes)
                self.assertEqual(request.status, "BAD_REQUEST")

    def testMinimalRequest(self) -> None:
        requestBytes = b"GET /index.html HTTP/1.1\r\n\r\n"
        
        request = Request(requestBytes)
        self.assertRequestEquals(request, "GET", "/index.html", {}, "HTTP/1.1", {}, "")

    def testMethod(self) -> None:
        requestBytes = b"POST /index.html HTTP/1.1\r\n\r\n"
        
        request = Request(requestBytes)
        self.assertRequestEquals(request, "POST", "/index.html", {}, "HTTP/1.1", {}, "")

    def testUrlEncodedPath(self) -> None:
        requestBytes = b"GET %2f%69%6e%64%65%78%2e%68%74%6d%6c HTTP/1.1\r\n\r\n"
        
        request = Request(requestBytes)
        self.assertRequestEquals(request, "GET", "/index.html", {}, "HTTP/1.1", {}, "")

    def testUrlEncodedPercent(self) -> None:
        requestBytes = b"GET %25%32%35 HTTP/1.1\r\n\r\n"
        
        request = Request(requestBytes)
        self.assertRequestEquals(request, "GET", "%25", {}, "HTTP/1.1", {}, "")

    def testNoValueQuery(self) -> None:
        requestBytes = b"GET /index.html?q HTTP/1.1\r\n\r\n"
        
        request = Request(requestBytes)
        self.assertRequestEquals(request, "GET", "/index.html", {"q": [None]}, "HTTP/1.1", {}, "")

    def testSingleQuery(self) -> None:
        requestBytes = b"GET /index.html?q=1 HTTP/1.1\r\n\r\n"
        
        request = Request(requestBytes)
        self.assertRequestEquals(request, "GET", "/index.html", {"q": ["1"]}, "HTTP/1.1", {}, "")

    def testMultipleQuery(self) -> None:
        requestBytes = b"GET /index.html?p=query1&q=query2 HTTP/1.1\r\n\r\n"
        
        request = Request(requestBytes)
        self.assertRequestEquals(request, "GET", "/index.html", {"p": ["query1"], "q": ["query2"]}, "HTTP/1.1", {}, "")

    def testDuplicateQuery(self) -> None:
        requestBytes = b"GET /index.html?p=1&p=2&p&p&p=3 HTTP/1.1\r\n\r\n"
        
        request = Request(requestBytes)
        self.assertRequestEquals(request, "GET", "/index.html", {"p": ["1", "2", None, None, "3"]}, "HTTP/1.1", {}, "")

    def testNoValueHeader(self) -> None:
        requestBytes = b"GET /index.html HTTP/1.1\r\nHost:\r\n\r\n"
        
        request = Request(requestBytes)
        self.assertRequestEquals(request, "GET", "/index.html", {}, "HTTP/1.1", {"Host": [None]}, "")

    def testSingleHeader(self) -> None:
        requestBytes = b"GET /index.html HTTP/1.1\r\nHost: localhost\r\n\r\n"
        
        request = Request(requestBytes)
        self.assertRequestEquals(request, "GET", "/index.html", {}, "HTTP/1.1", {"Host": ["localhost"]}, "")

    def testMultipleHeader(self) -> None:
        requestBytes = b"GET /index.html HTTP/1.1\r\nHost: localhost\r\nHeader: Value\r\n\r\n"
        
        request = Request(requestBytes)
        self.assertRequestEquals(request, "GET", "/index.html", {}, "HTTP/1.1", {"Host": ["localhost"], "Header": ["Value"]}, "")

    def testDuplicateHeader(self) -> None:
        requestBytes = b"GET /index.html HTTP/1.1\r\nHeader: Value1\r\nHeader: Value2\r\n\r\n"
        
        request = Request(requestBytes)
        self.assertRequestEquals(request, "GET", "/index.html", {}, "HTTP/1.1", {"Header": ["Value1", "Value2"]}, "")

    def testBody(self) -> None:
        requestBytes = b"GET /index.html HTTP/1.1\r\n\r\nBody Text"
        
        request = Request(requestBytes)
        self.assertRequestEquals(request, "GET", "/index.html", {}, "HTTP/1.1", {}, "Body Text")

    def testFullRequest(self) -> None:
        requestBytes = b"POST /%69%6e%64%65%78.html?%69=%69%20%69&q&q=1 HTTP/1.1\r\nHost: localhost\r\nContent-Length: 22\r\n\r\nThis is 22 characters."
        
        request = Request(requestBytes)
        self.assertRequestEquals(request, "POST", "/index.html", {"i": ["i i"], "q": [None, "1"]}, "HTTP/1.1", {"Host": ["localhost"], "Content-Length": ["22"]}, "This is 22 characters.")