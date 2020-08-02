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
    pass


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
  - experiment_type: labctl.experiment.tests.test_sequence.TestExperiment
"""
        )

        self.assertEquals(len(sequence.experiments), 2)

        first_experiment = sequence.experiments[0]
        self.assertIsInstance(first_experiment, TestExperiment)
