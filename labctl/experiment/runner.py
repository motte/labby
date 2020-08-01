from typing import Sequence

from labctl.config import Config
from labctl.experiment import Experiment, BaseInputParameters, BaseOutputData


class ExperimentRunner:
    config: Config
    sequence: Sequence[Experiment[BaseInputParameters, BaseOutputData]]

    def __init__(
        self,
        config: Config,
        sequence: Sequence[Experiment[BaseInputParameters, BaseOutputData]],
    ):
        self.config = config
        self.sequence = sequence

    def run(self) -> None:
        for experiment in self.sequence:
            self.run_experiment(experiment)

    def run_experiment(
        self, experiment: Experiment[BaseInputParameters, BaseOutputData]
    ) -> None:
        pass
