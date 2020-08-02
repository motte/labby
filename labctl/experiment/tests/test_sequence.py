from dataclasses import dataclass
from unittest import TestCase

from labctl.experiment import (
    BaseInputParameters,
    BaseOutputData,
    Experiment,
)
from labctl.experiment.sequence import ExperimentSequence


@dataclass(frozen=True)
class OutputData(BaseOutputData):
    pass


@dataclass(frozen=True)
class InputParameters(BaseInputParameters):
    current_in_amps: float
    voltage_in_volts: float = 6


class TestExperiment(Experiment[InputParameters, OutputData]):
    SAMPLING_RATE_IN_HZ: float = 1.0
    DURATION_IN_SECONDS: float = 3600

    def start(self) -> None:
        pass

    def measure(self) -> OutputData:
        return OutputData()

    def stop(self) -> None:
        pass


class ExperimentSequenceTest(TestCase):
    def test_parsing(self) -> None:
        sequence = ExperimentSequence(
            """
---
sequence:
  - experiment_type: labctl.experiment.tests.test_sequence.TestExperiment
    params:
      current_in_amps: 7
  - experiment_type: labctl.experiment.tests.test_sequence.TestExperiment
    params:
      current_in_amps: 3
      voltage_in_volts: 2
"""
        )

        self.assertEquals(len(sequence.experiments), 2)

        first_experiment = sequence.experiments[0]
        self.assertIsInstance(first_experiment, TestExperiment)
        self.assertAlmostEquals(first_experiment.params.current_in_amps, 7)
        self.assertAlmostEquals(first_experiment.params.voltage_in_volts, 6)

        second_experiment = sequence.experiments[1]
        self.assertIsInstance(second_experiment, TestExperiment)
        self.assertAlmostEquals(second_experiment.params.current_in_amps, 3)
        self.assertAlmostEquals(second_experiment.params.voltage_in_volts, 2)
