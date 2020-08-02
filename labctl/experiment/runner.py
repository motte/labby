import time

from labctl.config import Config
from labctl.experiment import Experiment, BaseInputParameters, BaseOutputData


class ExperimentRunner:
    config: Config
    experiment: Experiment[BaseInputParameters, BaseOutputData]
    has_started = False

    def __init__(
        self,
        config: Config,
        experiment: Experiment[BaseInputParameters, BaseOutputData],
    ):
        self.config = config
        self.experiment = experiment

    def run_experiment(self) -> None:
        assert not self.has_started
        self.has_started = True
        self.experiment.start()
        try:
            start_time = time.time()
            now = start_time

            while now - start_time <= self.experiment.DURATION_IN_SECONDS:
                self.experiment.measure()

                elapsed = time.time() - now
                time.sleep(1.0 / self.experiment.SAMPLING_RATE_IN_HZ - elapsed)
                now = time.time()
        finally:
            self.experiment.stop()
