from queue import Queue
from socket import socket
from threading import Thread
from unittest import TestCase

from protoserver.config import Config
from protoserver.servers.socket import SocketConnection, SocketServer


class testSocketConnection(TestCase):

    def setUp(self) -> None:
        c = Config.getMinimalValidConfig({"SERVER": "SocketServer", "HOSTNAME": "localhost", "PORT": "80"})
        try:
            self.s = SocketServer(c)
        except PermissionError:
            self.skipTest("Permission Error")
        self.c: Queue[SocketConnection] = Queue()
        
        self.clientConns: list[socket] = []

        self.serverThread = Thread(target = self.runServer)
        self.serverThread.start()

    def runServer(self) -> None:
        while True:
            conn = self.s.accept()
            if conn is None:
                break
            self.c.put(conn)

    def tearDown(self) -> None:
        self.s.stop()
        del self.s
        del self.c

        self.serverThread.join()
        del self.serverThread

        for conn in self.clientConns:
            conn.close()
        del self.clientConns


    def getClientConn(self) -> socket:
        clientConn = socket()
        self.clientConns.append(clientConn)
        clientConn.connect(("localhost", 80))
        return clientConn

    def testAccept(self) -> None:
        clientConn = self.getClientConn()

        serverConn = self.c.get()

    def testRecv(self) -> None:
        clientConn = self.getClientConn()

        serverConn = self.c.get()

        clientConn.send(b"Request Bytes")
        self.assertEqual(serverConn.recv(), b"Request Bytes")

    def testSend(self) -> None:
        clientConn = self.getClientConn()

        serverConn = self.c.get()

        serverConn.send(b"Response Bytes")
        self.assertEqual(clientConn.recv(8192), b"Response Bytes")

    def testClientClose(self) -> None:
        clientConn = self.getClientConn()

        serverConn = self.c.get()

        clientConn.close()
        self.assertEqual(serverConn.recv(), b"")

    def testServerClose(self) -> None:
        clientConn = self.getClientConn()

        serverConn = self.c.get()

        serverConn.close()
        self.assertEqual(clientConn.recv(8192), b"")

    def testMultipleConnections(self) -> None:
        clientConn1 = self.getClientConn()
        clientConn2 = self.getClientConn()

        serverConn1 = self.c.get()
        serverConn2 = self.c.get()

        clientConn1.send(b"Request Bytes 1")
        clientConn2.send(b"Request Bytes 2")
        serverConn1.send(b"Response Bytes 1")
        serverConn2.send(b"Response Bytes 2")

        self.assertEqual(clientConn1.recv(8192), b"Response Bytes 1")
        self.assertEqual(clientConn2.recv(8192), b"Response Bytes 2")
        self.assertEqual(serverConn1.recv(), b"Request Bytes 1")
        self.assertEqual(serverConn2.recv(), b"Request Bytes 2")