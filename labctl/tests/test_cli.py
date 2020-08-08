import re
from time import sleep as sleep_orig
from pathlib import PosixPath
from typing import List, Tuple
from unittest import TestCase
from unittest.mock import call, patch, Mock

from labctl import cli
from labctl.tests.utils import (
    captured_output,
    cli_arguments,
    environment_variable,
    fake_serial_port,
    labctl_config,
    patch_file_contents,
)


LABCTL_CONFIG = """
---
devices:
  - name: "zup-6-132"
    type: power_supply
    driver: labctl.hw.tdklambda.power_supply.ZUP
    args:
      port: "/dev/ttyUSB0"
      baudrate: 9600
      address: 1
"""


def _strip_colors(output: str) -> str:
    return re.sub(r"\x1b[0-9;[]+[mGK]", "", output)


class CommandLineTest(TestCase):
    def main(self, arguments: List[str]) -> Tuple[int, str, str]:
        rc = 0
        with cli_arguments(arguments), captured_output() as (
            stdout,
            stderr,
        ), environment_variable("WASABI_LOG_FRIENDLY", "1"):
            try:
                cli.main()
            except SystemExit as ex:
                rc = ex.code
        return (rc, _strip_colors(stdout.getvalue()), stderr.getvalue())

    def test_easter_egg(self) -> None:
        with labctl_config(LABCTL_CONFIG):
            (rc, stdout, _stderr) = self.main(["hello"])
        self.assertEqual(rc, 0)
        self.assertEqual(stdout, "Hello world\n")

    def test_command_is_required(self) -> None:
        (rc, stdout, stderr) = self.main([])
        self.assertEqual(rc, 2)
        self.assertTrue("usage: labctl" in stderr)
        self.assertTrue(
            "labctl: error: the following arguments are required: command\n" in stderr
        )

    def test_invalid_command(self) -> None:
        (rc, stdout, stderr) = self.main(["foobar"])
        self.assertTrue("usage: labctl" in stderr)
        self.assertTrue("labctl: error: argument command: invalid choice" in stderr)
        self.assertEqual(rc, 2)

    @fake_serial_port
    def test_list_devices(self, serial_port_mock: Mock) -> None:
        serial_port_mock.readline.return_value = b"FOOBAR\r\n"

        with labctl_config(LABCTL_CONFIG):
            (rc, stdout, stderr) = self.main(["devices"])
        self.assertEqual(rc, 0)
        self.assertIn("[+] zup-6-132", stdout)

    @fake_serial_port
    def test_list_unavailable_devices(self, serial_port_mock: Mock) -> None:
        with labctl_config(LABCTL_CONFIG):
            (rc, stdout, stderr) = self.main(["devices"])
        self.assertEqual(rc, 0)
        self.assertIn("[x] zup-6-132", stdout)

    def test_run_without_sequence_file(self) -> None:
        with labctl_config(LABCTL_CONFIG):
            (rc, stdout, stderr) = self.main(["run"])
        self.assertEqual(rc, 2)
        self.assertTrue("usage: labctl" in stderr)
        self.assertTrue(
            "labctl run: error: the following arguments are required:"
            + " sequence_filename\n"
            in stderr
        )

    @fake_serial_port
    def test_run_sequence(self, serial_port_mock: Mock) -> None:
        serial_port_mock.readline.return_value = b"AV2.0\r\n"
        import labctl.tests.test_experiment  # noqa

        SEQUENCE_CONTENTS = """
---
sequence:
  - experiment_type: labctl.tests.test_experiment.TestExperiment
  - experiment_type: labctl.tests.test_experiment.TestExperiment
"""
        with labctl_config(LABCTL_CONFIG), patch_file_contents(
            "sequence/test.yml", SEQUENCE_CONTENTS
        ), patch_file_contents("output/test/000.csv") as output_0, patch_file_contents(
            "output/test/001.csv"
        ) as output_1, patch(
            "os.makedirs"
        ) as makedirs, patch(
            "time.sleep", side_effect=sleep_orig
        ):
            # TODO remove time.sleep patch and make these tests less dependent on time
            # and less hacky
            (rc, stdout, stderr) = self.main(["run", "sequence/test.yml"])
            makedirs.assert_called_with(PosixPath("output/test/"), exist_ok=True)
            output_0.write.assert_has_calls(
                # TODO check second datapoint too
                [call("seconds,voltage\n"), call("0.0,2.0\n")]
            )
            output_1.write.assert_has_calls(
                # TODO check second datapoint too
                [call("seconds,voltage\n"), call("0.0,2.0\n")]
            )
        self.assertEqual(rc, 0)
