import time
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
        experiment.start()
        try:
            start_time = time.time()
            now = start_time

            while now - start_time <= experiment.DURATION_IN_SECONDS:
                experiment.measure()

                elapsed = time.time() - now
                time.sleep(1.0 / experiment.SAMPLING_RATE_IN_HZ - elapsed)
                now = time.time()
        finally:
            experiment.stop()
