from unittest import TestCase
from labctl import cli
from labctl.tests.utils import captured_output


class CommandLineTest(TestCase):
    def test_basic_instantiation(self):
        with captured_output() as (stdout, _stderr):
            cli.main()
        self.assertEqual(stdout.getvalue(), "Hello world\n")
