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


TOutputData = TypeVar("TOutputData", bound=BaseOutputData, covariant=True)
TInputParameters = TypeVar(
    "TInputParameters", bound=BaseInputParameters, covariant=True
)


class Experiment(Generic[TInputParameters, TOutputData], ABC):
    params: TInputParameters

    def __init__(self, params: TInputParameters) -> None:
        self.params = params

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def measure(self) -> TOutputData:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError
