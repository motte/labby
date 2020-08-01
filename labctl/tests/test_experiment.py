from dataclasses import dataclass
from unittest import TestCase
from unittest.mock import patch

from labctl.config import Config
from labctl.experiment import (
    BaseInputParameters,
    BaseOutputData,
    Experiment,
)
from labctl.experiment.runner import ExperimentRunner


@dataclass(frozen=True)
class OutputData(BaseOutputData):
    pass


@dataclass(frozen=True)
class InputParameters(BaseInputParameters):
    sampling_rate_in_hz: float = 1.0
    duration_in_seconds: float = 3600


class TestExperiment(Experiment[InputParameters, OutputData]):
    def start(self) -> None:
        pass

    def measure(self) -> OutputData:
        return OutputData()

    def stop(self) -> None:
        pass


class ExperimentInputOutputTest(TestCase):
    def test_input_parameters_instantiation(self) -> None:
        params = InputParameters()
        self.assertAlmostEquals(params.sampling_rate_in_hz, 1.0)
        self.assertAlmostEquals(params.duration_in_seconds, 3600)

    def test_output_data_instantiation(self) -> None:
        with patch("labctl.experiment.time.time", return_value=42):
            output = OutputData()
            self.assertAlmostEquals(output.seconds, 42)

        with patch("labctl.experiment.time.time", return_value=43):
            output = OutputData()
            self.assertAlmostEquals(output.seconds, 43)


class ExperimentRunnerTest(TestCase):
    config: Config

    def setUp(self) -> None:
        self.config = Config(
            """
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
        )

    def test_run_single_experiment(self) -> None:
        input_parameters = InputParameters(sampling_rate_in_hz=1, duration_in_seconds=3)
        experiment = TestExperiment(input_parameters)

        runner = ExperimentRunner(self.config)
        runner.run_sequence([experiment])
