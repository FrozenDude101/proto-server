from queue import Queue
from socket import socket
from threading import Thread
from unittest import TestCase

from protoserver.config import Config
from protoserver.servers.socket import SocketConnection, SocketServer

class testSocketServer(TestCase):

    def setUp(self) -> None:
        c = Config.getMinimalValidConfig({"SERVER": "SocketServer", "HOSTNAME": "localhost", "PORT": "80"})
        self.s = SocketServer(c)
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

    def testInvalidConfig(self) -> None:
        
        with self.subTest("A"):
            c = Config.getMinimalValidConfig({"SERVER": "SocketServer"})
            self.assertRaises(KeyError, lambda: SocketServer(c))

        with self.subTest("B"):
            c = Config.getMinimalValidConfig({"SERVER": "SocketServer", "HOSTNAME": "localhost"})
            self.assertRaises(KeyError, lambda: SocketServer(c))

        with self.subTest("C"):
            c = Config.getMinimalValidConfig({"SERVER": "SocketServer", "PORT": "22"})
            self.assertRaises(KeyError, lambda: SocketServer(c))

        with self.subTest("D"):
            c = Config.getMinimalValidConfig({"SERVER": "SocketServer", "HOSTNAME": "localhost", "PORT": "abc"})
            self.assertRaises(ValueError, lambda: SocketServer(c))

        with self.subTest("E"):
            c = Config.getMinimalValidConfig({"SERVER": "SocketServer", "HOSTNAME": "localhost", "PORT": "-1"})
            self.assertRaises(OverflowError, lambda: SocketServer(c))

        with self.subTest("F"):
            c = Config.getMinimalValidConfig({"SERVER": "SocketServer", "HOSTNAME": "localhost", "PORT": "65536"})
            self.assertRaises(OverflowError, lambda: SocketServer(c))

    def testServerStop(self) -> None:
        clientConn = self.getClientConn()

        self.c.get()

        self.s.stop()

        self.assertEqual(clientConn.recv(8192), b"")