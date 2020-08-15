import threading
import time

import pandas

from labby.config import Config
from labby.experiment import Experiment, BaseInputParameters, BaseOutputData


class ExperimentRunner(threading.Thread):
    config: Config
    experiment: Experiment[BaseInputParameters, BaseOutputData]
    dataframe: pandas.DataFrame

    def __init__(
        self,
        config: Config,
        experiment: Experiment[BaseInputParameters, BaseOutputData],
    ) -> None:
        super().__init__()
        self.config = config
        self.experiment = experiment
        # TODO find a better place for this assignment
        self.experiment.config = self.config
        column_names = ["seconds"] + list(
            experiment.get_output_data_type().get_column_names()
        )
        self.dataframe = pandas.DataFrame(columns=column_names)

    def run(self) -> None:
        self.experiment.start()
        try:
            start_time = time.time()
            now = start_time
            period_in_sec = 1.0 / self.experiment.SAMPLING_RATE_IN_HZ

            while now - start_time <= self.experiment.DURATION_IN_SECONDS:
                output_data = self.experiment.measure()
                raw_data = {
                    key: getattr(output_data, key)
                    for key in output_data.get_column_names()
                }
                self.dataframe = self.dataframe.append(
                    {"seconds": (now - start_time), **raw_data}, ignore_index=True
                )

                time.sleep(period_in_sec - (time.time() - start_time) % period_in_sec)
                now = time.time()
        finally:
            self.experiment.stop()
