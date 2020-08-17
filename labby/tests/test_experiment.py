from dataclasses import dataclass
from pathlib import PosixPath
from typing import List
from unittest import TestCase
from unittest.mock import call, patch

from pynng import Sub0

from labby.config import Config
from labby.experiment import (
    BaseInputParameters,
    BaseOutputData,
    Experiment,
)
from labby.experiment.sequence import ExperimentSequence
from labby.experiment.runner import (
    ExperimentRunner,
    ExperimentSequenceStatus,
    ExperimentState,
    ExperimentStatus,
)
from labby.tests.utils import patch_file_contents, patch_time
from labby.utils import auto_discover_drivers


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


LABBY_CONFIG_YAML = """
---
devices:
  - name: "virtual-power-supply"
    type: power_supply
    driver: labby.hw.virtual.power_supply.PowerSupply
    args:
      load_in_ohms: 5
"""

SEQUENCE_YAML = """
---
sequence:
  - experiment_type: labby.tests.test_experiment.TestExperiment
"""


class ExperimentRunnerTest(TestCase):
    def setUp(self) -> None:
        auto_discover_drivers()

    def test_output_data_type_metadata(self) -> None:
        input_parameters = InputParameters()
        experiment = TestExperiment("test_experiment", input_parameters)
        output_data_type = experiment.get_output_data_type()
        self.assertEqual(output_data_type.get_column_names(), ["voltage"])

    def test_experiment_output(self) -> None:
        config = Config(LABBY_CONFIG_YAML)
        sequence = ExperimentSequence("./sequences/seq.yaml", SEQUENCE_YAML)
        runner = ExperimentRunner(config, sequence)

        with patch_time("2020-08-08"), patch_file_contents(
            "output/seq/000.csv"
        ) as output, patch("os.makedirs") as makedirs:
            runner.start()
            runner.join()

        makedirs.assert_called_with(PosixPath("output/seq/"), exist_ok=True)
        self.assertEqual(len(output.write.call_args_list), 4)
        output.write.assert_has_calls(
            [
                call("seconds,voltage\n"),
                call("0.0,15.0\n"),
                call("0.5,15.0\n"),
                call("1.0,15.0\n"),
            ]
        )

    def test_published_messages(self) -> None:
        config = Config(LABBY_CONFIG_YAML)
        sequence = ExperimentSequence("./sequences/seq.yaml", SEQUENCE_YAML)
        runner = ExperimentRunner(config, sequence)

        with Sub0(dial=runner.subscription_address) as sub:
            sub.subscribe(b"")
            received_messages: List[ExperimentSequenceStatus] = []

            with patch_time("2020-08-08"), patch_file_contents(
                "output/seq/000.csv"
            ), patch("os.makedirs"):
                runner.start()
                while True:
                    msg = sub.recv()
                    status = ExperimentSequenceStatus.from_msgpack(msg)
                    received_messages.append(status)
                    if status.is_finished():
                        break
                runner.join()

            self.assertEqual(
                received_messages,
                [
                    ExperimentSequenceStatus(
                        experiments=[
                            ExperimentStatus(
                                name="000", state=ExperimentState.RUNNING, progress=0.0,
                            )
                        ]
                    ),
                    ExperimentSequenceStatus(
                        experiments=[
                            ExperimentStatus(
                                name="000", state=ExperimentState.RUNNING, progress=0.0,
                            )
                        ]
                    ),
                    ExperimentSequenceStatus(
                        experiments=[
                            ExperimentStatus(
                                name="000", state=ExperimentState.RUNNING, progress=0.5,
                            )
                        ]
                    ),
                    ExperimentSequenceStatus(
                        experiments=[
                            ExperimentStatus(
                                name="000", state=ExperimentState.RUNNING, progress=1.0,
                            )
                        ]
                    ),
                    ExperimentSequenceStatus(
                        experiments=[
                            ExperimentStatus(
                                name="000",
                                state=ExperimentState.FINISHED,
                                progress=1.0,
                            )
                        ]
                    ),
                ],
            )
