import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar


def experiment_data(cls=None):
    def wrap(cls):
        return dataclass(cls, frozen=True)

    return wrap if cls is None else wrap(cls)


@dataclass(frozen=True)
class BaseOutputData:
    seconds: float = time.time()

    def __post_init__(self):
        super().__setattr__("seconds", time.time())


@dataclass(frozen=True)
class BaseInputParameters:
    sampling_rate_in_hz: float
    duration_in_seconds: float


experiment_output_data = experiment_data
experiment_input_parameters = experiment_data
