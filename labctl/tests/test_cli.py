from unittest import TestCase
from typing import List, Tuple

from labctl import cli
from labctl.tests.utils import captured_output, cli_arguments


class CommandLineTest(TestCase):
    def main(self, arguments: List[str]) -> Tuple[str, str]:
        with cli_arguments(arguments), captured_output() as (stdout, stderr):
            cli.main()
        return (stdout.getvalue(), stderr.getvalue())

    def test_easter_egg(self):
        (stdout, stderr) = self.main(["--hello"])
        self.assertEqual(stdout, "Hello world\n")
