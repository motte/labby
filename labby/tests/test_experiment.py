from dataclasses import dataclass
from unittest import TestCase

from labby.config import Config
from labby.experiment import (
    BaseInputParameters,
    BaseOutputData,
    Experiment,
)
from labby.experiment.runner import ExperimentRunner
from labby.tests.utils import patch_time
from labby.hw.core import auto_discover_drivers


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


class ExperimentRunnerTest(TestCase):
    def setUp(self) -> None:
        auto_discover_drivers()

    def test_output_data_type_metadata(self) -> None:
        input_parameters = InputParameters()
        experiment = TestExperiment("test_experiment", input_parameters)
        output_data_type = experiment.get_output_data_type()
        self.assertEquals(output_data_type.get_column_names(), ["voltage"])

    def test_run_single_experiment(self) -> None:
        config = Config(LABBY_CONFIG_YAML)

        input_parameters = InputParameters()
        experiment = TestExperiment("test_experiment", input_parameters)

        runner = ExperimentRunner(config, experiment)

        with patch_time("2020-08-08"):
            runner.run_experiment()

        dataframe = runner.dataframe
        self.assertEquals(dataframe.columns.to_list(), ["seconds", "voltage"])
        self.assertEquals(dataframe["seconds"].to_list(), [0.0, 0.5, 1.0])
        self.assertEquals(dataframe["voltage"].to_list(), [15.0, 15.0, 15.0])

        with self.assertRaises(AssertionError):
            # cannot run the same experiment again with the same ExperimentRunner
            runner.run_experiment()
