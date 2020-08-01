from unittest import TestCase
from unittest.mock import patch

from labctl.experiment import (
    BaseInputParameters,
    BaseOutputData,
    Experiment,
    experiment_input_parameters,
    experiment_output_data,
)


@experiment_output_data
class OutputData(BaseOutputData):
    pass


@experiment_input_parameters
class InputParameters(BaseInputParameters):
    sampling_rate_in_hz: float = 1.0
    duration_in_seconds: float = 3600


class TestExperiment(Experiment[InputParameters, OutputData]):
    def start(self) -> None:
        raise NotImplementedError

    def measure(self) -> OutputData:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError


class ExperimentTest(TestCase):
    def test_input_parameters_instantiation(self) -> None:
        # pyre-ignore[20]: pyre doesn't seem to be aware of dataclass inheritance
        params = InputParameters()
        self.assertAlmostEquals(params.sampling_rate_in_hz, 1.0)
        self.assertAlmostEquals(params.duration_in_seconds, 3600)

        with patch("labctl.experiment.time.time", return_value=43):
            output = OutputData()
            self.assertAlmostEquals(output.seconds, 43)

    def test_output_data_instantiation(self) -> None:
        with patch("labctl.experiment.time.time", return_value=42):
            output = OutputData()
            self.assertAlmostEquals(output.seconds, 42)

        with patch("labctl.experiment.time.time", return_value=43):
            output = OutputData()
            self.assertAlmostEquals(output.seconds, 43)
