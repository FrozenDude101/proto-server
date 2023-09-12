from unittest import TestCase

from protoserver.config import Config
from protoserver.servers.function import FunctionServer


class TestConfig(TestCase):

    def testNoServerAttribute(self) -> None:
        c = {"HANDLER": "HTMLMirrorHandler"}
        self.assertRaises(ValueError, lambda: Config(c))

    def testInvalidServerAttribute(self) -> None:
        c = {"SERVER": "InvalidServer", "HANDLER": "HTMLMirrorHandler"}
        self.assertRaises(ValueError, lambda: Config(c))

    def testValidServerAttribute(self) -> None:
        c = Config.MINIMAL_VALID_CONFIG_OPTIONS
        self.assertEqual(Config(c).getServer(), FunctionServer)

    def testInvalidAttribute(self) -> None:
        c = Config.MINIMAL_VALID_CONFIG_OPTIONS
        self.assertRaises(KeyError, lambda: Config(c).get("InvalidAttribute"))

    def testNoneAttribute(self) -> None:
        c = Config.MINIMAL_VALID_CONFIG_OPTIONS | {"NoneAttribute": None}
        self.assertRaises(ValueError, lambda: Config(c).get("NoneAttribute"))

    def testValidAttribute(self) -> None:
        c = Config.MINIMAL_VALID_CONFIG_OPTIONS | {"ValidAttribute": "Value"}
        self.assertEqual(Config(c).get("ValidAttribute"), "Value")

    def testValidAttributeTypeCast(self) -> None:
        c = Config.MINIMAL_VALID_CONFIG_OPTIONS | {"IntAttribute": "1"}
        self.assertEqual(Config(c).get("IntAttribute", int), 1)
