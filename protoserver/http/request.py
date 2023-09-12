from __future__ import annotations
from typing import Literal


_Context = Literal["START", "METHOD", "PATH", "QUERYNAME", "QUERYVALUE", "VERSION", "SKIPCHECK", "SKIP", "HEADERNAME", "HEADERVALUE", "BODY"]
_Token = tuple[_Context, bytes]

class Request(object):

    def __init__(self, requestBytes: bytes) -> None:

        self.status = "OK"
        self.raw = requestBytes
        
        readBytes: list[bytes] = []
        tokens: list[_Token] = []
        byteContext: _Context = "START"
        for byte in map(lambda b: chr(b).encode(), requestBytes):
            readBytes.append(byte)

            res = self._parseReadBytes(byteContext, readBytes)
            if res is None:
                continue

            byteContext = res[0]
            if res[1] is not None:
                tokens.append(res[1])

        if byteContext != "BODY":
            self.status = "BAD_REQUEST"

        self.headers = {}
        self.queries = {}

        try:
            self._parseTokens(tokens)
        except Exception as e:
            print(e)
            self.status = "BAD_REQUEST"
            return
        
        self._parseBody(readBytes)

    def _parseReadBytes(self, context: _Context, readBytes: list[bytes]) -> None | tuple[_Context, None | _Token]:
        match (context):
            case "START":
                match (readBytes):
                    case [b"\r", b"\n"]:
                        readBytes.clear()
                        return "START", None
                    case _:
                        return "METHOD", None
                    
            case "METHOD":
                match (readBytes):
                    case [*b, b" "]:
                        readBytes.clear()
                        return "PATH", ("METHOD", b"".join(b))
                    
            case "PATH":
                match (readBytes):
                    case [*b, b"?"]:
                        readBytes.clear()
                        return "QUERYNAME", ("PATH", b"".join(b))
                    case [*b, b" "]:
                        readBytes.clear()
                        return "VERSION", ("PATH", b"".join(b))
                    case [*b, b"\r", b"\n"]:
                        readBytes.clear()
                        return "SKIPCHECK", ("PATH", b"".join(b))
                    
            case "QUERYNAME":
                match (readBytes):
                    case [*b, b"&"]:
                        readBytes.clear()
                        return "QUERYNAME", ("QUERYNAME", b"".join(b))
                    case [*b, b"="]:
                        readBytes.clear()
                        return "QUERYVALUE", ("QUERYNAME", b"".join(b))
                    case [*b, b" "]:
                        readBytes.clear()
                        return "VERSION", ("QUERYNAME", b"".join(b))
                    case [*b, b"\r", b"\n"]:
                        readBytes.clear()
                        return "SKIPCHECK", ("QUERYNAME", b"".join(b))
                        
            case "QUERYVALUE":
                match (readBytes):
                    case [*b, b"&"]:
                        readBytes.clear()
                        return "QUERYNAME", ("QUERYVALUE", b"".join(b))
                    case [*b, b" "]:
                        readBytes.clear()
                        return "VERSION", ("QUERYVALUE", b"".join(b))
                    case [*b, b"\r", b"\n"]:
                        readBytes.clear()
                        return "SKIPCHECK", ("QUERYVALUE", b"".join(b))
                    
            case "VERSION":
                match (readBytes):
                    case [*b, b"\r", b"\n"]:
                        readBytes.clear()
                        return "SKIPCHECK", ("VERSION", b"".join(b))
                    
            case "SKIPCHECK":
                match (readBytes):
                    case [b" "]:
                        readBytes.clear()
                        return "SKIP", None
                    case [b"\r"]:
                        return
                    case [b"\r", b"\n"]:
                        readBytes.clear()
                        return "BODY", None
                    case _:
                        return "HEADERNAME", None
                    
            case "SKIP":
                match (readBytes):
                    case [*b, b"\r", b"\n"]:
                        readBytes.clear()
                        return "SKIPCHECK", None
                    
            case "HEADERNAME":
                match (readBytes):
                    case [*b, b":"]:
                        readBytes.clear()
                        return "HEADERVALUE", ("HEADERNAME", b"".join(b))
                    
            case "HEADERVALUE":
                match (readBytes):
                    case [b"\r", b"\n"]:
                        readBytes.clear()
                        return "SKIPCHECK", None
                    case [*b, b"\r", b"\n"]:
                        readBytes.clear()
                        return "SKIPCHECK", ("HEADERVALUE", b"".join(b))

    def _parseTokens(self, tokens: list[_Token]) -> None:
        
        t = tokens.pop(0)
        if t[0] != "METHOD": raise Exception
        self.method = self._decodeBytes(t[1]).strip()
        
        t = tokens.pop(0)
        if t[0] != "PATH": raise Exception
        self.path = self._decodeUrlEncodedBytes(t[1]).strip()

        t = tokens.pop(0)
        while t[0] == "QUERYNAME":
            qName = self._decodeUrlEncodedBytes(t[1]).strip()
            if qName not in self.queries:
                self.queries[qName] = []

            if not len(tokens): 
                self.queries[qName].append(None)
                return
            t = tokens.pop(0)

            if t[0] != "QUERYVALUE":
                self.queries[qName].append(None)
                continue
            qValue = self._decodeUrlEncodedBytes(t[1]).strip()
            self.queries[qName].append(qValue)
            if not len(tokens): return
            t = tokens.pop(0)

        if t[0] == "VERSION":
            self.version = self._decodeBytes(t[1]).strip()
            if not len(tokens): return
            t = tokens.pop(0)

        while t[0] == "HEADERNAME":
            hName = self._decodeBytes(t[1]).strip()
            if hName not in self.headers:
                self.headers[hName] = []

            if not len(tokens): 
                self.headers[hName].append(None)
                return
            t = tokens.pop(0)

            if t[0] != "HEADERVALUE":
                self.headers[hName].append(None)
                continue
            hValue = self._decodeBytes(t[1]).strip()
            self.headers[hName].append(hValue)
            
            if not len(tokens): return
            t = tokens.pop(0)

    def _parseBody(self, bodyBytes: list[bytes]) -> None:
        self.body = self._decodeBytes(b"".join(bodyBytes))
        # TODO, properly parse body using Transfer-Encoding, and Content-Length headers.

    def _decodeBytes(self, encodedBytes: bytes) -> str:
        return encodedBytes.decode("iso-8859-1")
    
    def _decodeUrlEncodedBytes(self, encodedBytes: bytes) -> str:
        urlEncodedString = self._decodeBytes(encodedBytes)
        decodedString = ""

        i = 0
        while i < len(urlEncodedString):
            char = urlEncodedString[i]

            if char != "%":
                decodedString += char
                i += 1
                continue

            decodedString += chr(int(urlEncodedString[i+1:i+3], 16))  
            i += 3

        return decodedString