from dataclasses import dataclass
from unittest import TestCase

from labctl.config import Config
from labctl.experiment import (
    BaseInputParameters,
    BaseOutputData,
    Experiment,
)
from labctl.experiment.runner import ExperimentRunner
from labctl.hw.core import auto_discover_drivers


@dataclass(frozen=True)
class OutputData(BaseOutputData):
    pass


@dataclass(frozen=True)
class InputParameters(BaseInputParameters):
    pass


class TestExperiment(Experiment[InputParameters, OutputData]):
    SAMPLING_RATE_IN_HZ: float = 2.0
    DURATION_IN_SECONDS: float = 1.0

    def start(self) -> None:
        pass

    def measure(self) -> OutputData:
        return OutputData()

    def stop(self) -> None:
        pass


class ExperimentRunnerTest(TestCase):
    config: Config

    def setUp(self) -> None:
        auto_discover_drivers()
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
        input_parameters = InputParameters()
        experiment = TestExperiment("test_experiment", input_parameters)

        runner = ExperimentRunner(self.config, experiment)
        runner.run_experiment()

        with self.assertRaises(AssertionError):
            # cannot run the same experiment again with the same ExperimentRunner
            runner.run_experiment()
