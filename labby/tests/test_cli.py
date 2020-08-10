import re
from dataclasses import dataclass
from pathlib import PosixPath
from typing import List, Tuple
from unittest import TestCase
from unittest.mock import call, patch

from labby import cli
from labby.experiment import (
    BaseInputParameters,
    BaseOutputData,
    Experiment,
)
from labby.tests.utils import (
    captured_output,
    cli_arguments,
    environment_variable,
    labby_config,
    patch_file_contents,
    patch_time,
)


LABBY_CONFIG = """
---
devices:
  - name: "virtual-power-supply"
    type: power_supply
    driver: labby.hw.virtual.power_supply.PowerSupply
    args:
      load_in_ohms: 5
  - name: "broken-power-supply"
    type: power_supply
    driver: labby.hw.virtual.power_supply.BrokenPowerSupply
    args:
      load_in_ohms: 5
"""


@dataclass(frozen=True)
class OutputData(BaseOutputData):
    voltage: float


@dataclass(frozen=True)
class InputParameters(BaseInputParameters):
    pass


class TestExperiment(Experiment[InputParameters, OutputData]):
    SAMPLING_RATE_IN_HZ: float = 2.0
    DURATION_IN_SECONDS: float = 1.0

    def start(self) -> None:
        power_supply = self.get_power_supply("virtual-power-supply")
        power_supply.set_target_voltage(15)
        power_supply.set_target_current(4)
        power_supply.set_output_on(True)
        power_supply.open()

    def measure(self) -> OutputData:
        power_supply = self.get_power_supply("virtual-power-supply")
        actual_voltage = power_supply.get_actual_voltage()
        return OutputData(voltage=actual_voltage)

    def stop(self) -> None:
        power_supply = self.get_power_supply("virtual-power-supply")
        power_supply.close()


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
        with labby_config(LABBY_CONFIG):
            (rc, stdout, _stderr) = self.main(["hello"])
        self.assertEqual(rc, 0)
        self.assertEqual(stdout, "Hello world\n")

    def test_command_is_required(self) -> None:
        (rc, stdout, stderr) = self.main([])
        self.assertEqual(rc, 2)
        self.assertTrue("usage: labby" in stderr)
        self.assertTrue(
            "labby: error: the following arguments are required: command\n" in stderr
        )

    def test_invalid_command(self) -> None:
        (rc, stdout, stderr) = self.main(["foobar"])
        self.assertTrue("usage: labby" in stderr)
        self.assertTrue("labby: error: argument command: invalid choice" in stderr)
        self.assertEqual(rc, 2)

    def test_list_devices(self) -> None:
        with labby_config(LABBY_CONFIG):
            (rc, stdout, stderr) = self.main(["devices"])
        self.assertEqual(rc, 0)
        self.assertIn("[+] virtual-power-supply", stdout)

    def test_list_unavailable_devices(self) -> None:
        with labby_config(LABBY_CONFIG):
            (rc, stdout, stderr) = self.main(["devices"])
        self.assertEqual(rc, 0)
        self.assertIn("[x] broken-power-supply", stdout)

    def test_run_without_sequence_file(self) -> None:
        with labby_config(LABBY_CONFIG):
            (rc, stdout, stderr) = self.main(["run"])
        self.assertEqual(rc, 2)
        self.assertTrue("usage: labby" in stderr)
        self.assertTrue(
            "labby run: error: the following arguments are required:"
            + " sequence_filename\n"
            in stderr
        )

    def test_run_sequence(self) -> None:
        SEQUENCE_CONTENTS = """
---
sequence:
  - experiment_type: labby.tests.test_cli.TestExperiment
  - experiment_type: labby.tests.test_cli.TestExperiment
"""
        with labby_config(LABBY_CONFIG), patch_file_contents(
            "sequence/test.yml", SEQUENCE_CONTENTS
        ), patch_file_contents("output/test/000.csv") as output_0, patch_file_contents(
            "output/test/001.csv"
        ) as output_1, patch(
            "os.makedirs"
        ) as makedirs, patch_time(
            "2020-08-08"
        ):
            (rc, stdout, stderr) = self.main(["run", "sequence/test.yml"])
            makedirs.assert_called_with(PosixPath("output/test/"), exist_ok=True)
            self.assertEquals(len(output_0.write.call_args_list), 4)
            output_0.write.assert_has_calls(
                [
                    call("seconds,voltage\n"),
                    call("0.0,15.0\n"),
                    call("0.5,15.0\n"),
                    call("1.0,15.0\n"),
                ]
            )
            output_1.write.assert_has_calls(
                [
                    call("seconds,voltage\n"),
                    call("0.0,15.0\n"),
                    call("0.5,15.0\n"),
                    call("1.0,15.0\n"),
                ]
            )
        self.assertEqual(rc, 0)

    def test_invalid_device_info(self) -> None:
        with labby_config(LABBY_CONFIG):
            (rc, stdout, stderr) = self.main(["device-info", "foobar"])
        self.assertEqual(rc, 1)
        self.assertIn("[x] Unknown device foobar", stdout)

    def test_available_device_info(self) -> None:
        with labby_config(LABBY_CONFIG):
            (rc, stdout, stderr) = self.main(["device-info", "virtual-power-supply"])
        self.assertEqual(rc, 0)
        self.assertIn("Connection       [+] OK", stdout)

    def test_device_that_cannot_be_opened(self) -> None:
        with patch(
            "labby.hw.virtual.power_supply.PowerSupply.open", side_effect=Exception
        ):
            with labby_config(LABBY_CONFIG):
                (rc, stdout, stderr) = self.main(
                    ["device-info", "virtual-power-supply"]
                )
        self.assertEqual(rc, 0)
        self.assertIn("Connection   [x] Error", stdout)

    def test_unavailable_device_info(self) -> None:
        with labby_config(LABBY_CONFIG):
            (rc, stdout, stderr) = self.main(["device-info", "broken-power-supply"])
        self.assertEqual(rc, 0)
        self.assertIn("Connection   [x] Error", stdout)
