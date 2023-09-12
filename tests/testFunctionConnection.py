from unittest import TestCase

from protoserver.config import Config
from protoserver.servers.function import FunctionServer


class testFunctionConnection(TestCase):

    def setUp(self) -> None:
        c = Config.getMinimalValidConfig()
        self.s = FunctionServer(c)
        self.s.accept()

    def tearDown(self) -> None:
        self.s.stop()
        del self.s

    def testClientSend(self) -> None:
        connection = self.s.getConnection()

        connection.clientSend(b"Request Bytes")
        self.assertEqual(connection.recv(), b"Request Bytes")

    def testClientRecv(self) -> None:
        connection = self.s.getConnection()

        connection.send(b"Response Bytes")
        self.assertEqual(connection.clientRecv(), b"Response Bytes")

    def testSequentialClientSend(self) -> None:
        connection = self.s.getConnection()

        connection.clientSend(b"Request Bytes 1")
        connection.clientSend(b"Request Bytes 2")
        self.assertEqual(connection.recv(), b"Request Bytes 1")
        self.assertEqual(connection.recv(), b"Request Bytes 2")

    def testSequentialClientRecv(self) -> None:
        connection = self.s.getConnection()

        connection.send(b"Response Bytes 1")
        connection.send(b"Response Bytes 2")
        self.assertEqual(connection.clientRecv(), b"Response Bytes 1")
        self.assertEqual(connection.clientRecv(), b"Response Bytes 2")

    def testMixedSendRecv(self) -> None:
        connection = self.s.getConnection()

        connection.clientSend(b"Request Bytes 1")
        connection.send(b"Response Bytes 1")
        self.assertEqual(connection.clientRecv(), b"Response Bytes 1")
        connection.clientSend(b"Request Bytes 2")
        connection.send(b"Response Bytes 2")
        self.assertEqual(connection.recv(), b"Request Bytes 1")
        self.assertEqual(connection.clientRecv(), b"Response Bytes 2")
        self.assertEqual(connection.recv(), b"Request Bytes 2")