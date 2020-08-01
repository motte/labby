from typing import Sequence

from labctl.config import Config
from labctl.experiment import Experiment, BaseInputParameters, BaseOutputData


class ExperimentRunner:
    config: Config

    def __init__(
        self, config: Config,
    ):
        self.config = config

    def run_sequence(
        self, sequence: Sequence[Experiment[BaseInputParameters, BaseOutputData]]
    ) -> None:
        for experiment in sequence:
            self.run_experiment(experiment)

    def run_experiment(
        self, experiment: Experiment[BaseInputParameters, BaseOutputData]
    ) -> None:
        pass
