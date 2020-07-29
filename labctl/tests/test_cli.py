from unittest import TestCase
from labctl import cli
from labctl.tests.utils import captured_output


class CommandLineTest(TestCase):
    def test_basic_instantiation(self):
        cli.main()
