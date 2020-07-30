from unittest import TestCase
from typing import List, Tuple

from labctl import cli
from labctl.tests.utils import captured_output, cli_arguments


class CommandLineTest(TestCase):
    def main(self, arguments: List[str]) -> Tuple[int, str, str]:
        rc = 0
        with cli_arguments(arguments), captured_output() as (stdout, stderr):
            try:
                cli.main()
            except SystemExit as ex:
                rc = ex.code
        return (rc, stdout.getvalue(), stderr.getvalue())

    def test_easter_egg(self):
        (rc, stdout, _stderr) = self.main(["hello"])
        self.assertEqual(rc, 0)
        self.assertEqual(stdout, "Hello world\n")

    def test_command_is_required(self):
        (rc, stdout, stderr) = self.main([])
        self.assertEqual(rc, 2)
        self.assertTrue("usage: labctl" in stderr)
        self.assertTrue(
            "labctl: error: the following arguments are required: command\n" in stderr
        )

    def test_invalid_command(self):
        (rc, stdout, stderr) = self.main(["foobar"])
        # TODO ehhh this should all go to stderr actually
        self.assertTrue("Error: Invalid command foobar\n" in stdout)
        self.assertTrue("usage: labctl" in stdout)
        self.assertEqual(rc, 2)
