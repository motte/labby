import math
import os
import threading
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List

import pandas
from mashumaro import DataClassMessagePackMixin
from pynng import Message, NNGException, Pub0

from labby.config import Config
from labby.experiment import Experiment, BaseInputParameters, BaseOutputData
from labby.experiment.sequence import ExperimentSequence


_ADDRESS = "inproc://experiment_runner"


class ExperimentState(Enum):
    NOT_STARTED = "NOT_STARTED"
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"


@dataclass(frozen=True)
class ExperimentStatus(DataClassMessagePackMixin):
    name: str
    state: ExperimentState
    progress: float

    def is_finished(self) -> bool:
        return self.state == ExperimentState.FINISHED


@dataclass(frozen=True)
class ExperimentSequenceStatus(DataClassMessagePackMixin):
    experiments: List[ExperimentStatus]

    def is_finished(self) -> bool:
        return all(experiment.is_finished() for experiment in self.experiments)


class ExperimentRunner(threading.Thread):
    subscription_address: str
    config: Config
    sequence: ExperimentSequence
    sequence_status: ExperimentSequenceStatus

    def __init__(self, config: Config, sequence: ExperimentSequence) -> None:
        super().__init__()
        self.config = config
        self.sequence = sequence
        self.subscription_address = _ADDRESS
        self.pub = Pub0(listen=self.subscription_address)
        self.sequence_status = ExperimentSequenceStatus(
            experiments=[
                ExperimentStatus(
                    name=experiment.name,
                    state=ExperimentState.NOT_STARTED,
                    progress=0.0,
                )
                for experiment in self.sequence.experiments
            ]
        )

    def _publish_status(
        self,
        experiment: Experiment[BaseInputParameters, BaseOutputData],
        relative_time: float,
    ) -> None:
        try:
            experiment_index = self.sequence.experiments.index(experiment)
            progress = relative_time / experiment.DURATION_IN_SECONDS
            self.sequence_status.experiments[experiment_index] = ExperimentStatus(
                name=experiment.name,
                state=ExperimentState.FINISHED
                if math.isclose(progress, 1.0)
                else ExperimentState.RUNNING,
                progress=progress,
            )

            msg = Message(self.sequence_status.to_msgpack())
            self.pub.send_msg(msg, block=False)
        except NNGException:
            pass

    def _get_output_directory(self) -> Path:
        sequence_name = Path(self.sequence.filename).stem
        return Path(f"./output/{sequence_name}/")

    def _run_experiment(
        self, experiment: Experiment[BaseInputParameters, BaseOutputData]
    ) -> pandas.DataFrame:
        column_names = ["seconds"] + list(
            experiment.get_output_data_type().get_column_names()
        )
        dataframe = pandas.DataFrame(columns=column_names)

        experiment.start()
        self._publish_status(experiment, 0.0)

        try:
            start_time = time.time()
            now = start_time
            period_in_sec = 1.0 / experiment.SAMPLING_RATE_IN_HZ

            while now - start_time <= experiment.DURATION_IN_SECONDS:
                self._publish_status(experiment, now - start_time)
                output_data = experiment.measure()
                raw_data = {
                    key: getattr(output_data, key)
                    for key in output_data.get_column_names()
                }
                dataframe = dataframe.append(
                    {"seconds": (now - start_time), **raw_data}, ignore_index=True
                )

                time.sleep(period_in_sec - (time.time() - start_time) % period_in_sec)
                now = time.time()
        finally:
            experiment.stop()
            self._publish_status(experiment, experiment.DURATION_IN_SECONDS)

            return dataframe

    def run(self) -> None:
        for experiment in self.sequence.experiments:
            # TODO find a better place for this assignment
            experiment.config = self.config

            dataframe = self._run_experiment(experiment)
            output_dir = self._get_output_directory()
            os.makedirs(output_dir, exist_ok=True)
            with open(output_dir / f"{experiment.name}.csv", "w") as fd:
                dataframe.to_csv(fd, index=False)
        self.pub.close()
