import time

import pandas

from labby.config import Config
from labby.experiment import Experiment, BaseInputParameters, BaseOutputData


class ExperimentRunner:
    config: Config
    experiment: Experiment[BaseInputParameters, BaseOutputData]
    dataframe: pandas.DataFrame
    has_started = False

    def __init__(
        self,
        config: Config,
        experiment: Experiment[BaseInputParameters, BaseOutputData],
    ) -> None:
        self.config = config
        self.experiment = experiment
        # TODO find a better place for this assignment
        self.experiment.config = self.config
        column_names = ["seconds"] + list(
            experiment.get_output_data_type().get_column_names()
        )
        self.dataframe = pandas.DataFrame(columns=column_names)

    def run_experiment(self) -> None:
        assert not self.has_started
        self.has_started = True
        self.experiment.start()
        try:
            start_time = time.time()
            now = start_time

            while now - start_time <= self.experiment.DURATION_IN_SECONDS:
                output_data = self.experiment.measure()
                raw_data = {
                    key: getattr(output_data, key)
                    for key in output_data.get_column_names()
                }
                self.dataframe = self.dataframe.append(
                    {"seconds": (now - start_time), **raw_data}, ignore_index=True
                )

                elapsed = time.time() - now
                time.sleep(1.0 / self.experiment.SAMPLING_RATE_IN_HZ - elapsed)
                now = time.time()
        finally:
            self.experiment.stop()
