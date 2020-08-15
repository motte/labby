import threading
import time

import pandas
from pynng import Message, NNGException, Pub0

from labby.config import Config
from labby.experiment import Experiment, BaseInputParameters, BaseOutputData


_ADDRESS = "inproc://experiment_runner"


class ExperimentRunner(threading.Thread):
    subscription_address: str
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
        self.subscription_address = _ADDRESS
        self.pub = Pub0(listen=self.subscription_address)

    def _publish(self, msg: bytes) -> None:
        try:
            self.pub.send_msg(Message(msg), block=False)
        except NNGException:
            pass

    def run(self) -> None:
        self._publish(b"starting")
        self.experiment.start()
        self._publish(b"started")

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

                self._publish(b"measured")
                time.sleep(period_in_sec - (time.time() - start_time) % period_in_sec)
                now = time.time()
        finally:
            self._publish(b"finished")
            self.experiment.stop()
            self.pub.close()
