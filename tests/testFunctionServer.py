from unittest import TestCase

from protoserver.config import Config
from protoserver.servers.function import FunctionServer

class testFunctionServer(TestCase):

    def setUp(self) -> None:
        c = Config.getMinimalValidConfig()
        self.s = FunctionServer(c)

    def tearDown(self) -> None:
        self.s.stop()
        del self.s

    def testFirstConnectionIsSetConnection(self) -> None:
        connection = self.s.accept()
        self.assertEqual(connection, self.s.getConnection())

    def testNoneAfterFirstConnection(self) -> None:
        self.s.accept()
        secondConnection = self.s.accept()
        self.assertIsNone(secondConnection)