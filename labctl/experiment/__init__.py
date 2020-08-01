import inspect
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Generic, Optional, Type, TypeVar, get_args


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


ALL_EXPERIMENTS: Dict[str, Type["Experiment"]] = {}


class Experiment(Generic[TInputParameters, TOutputData], ABC):
    params: TInputParameters

    def __init__(self, params: TInputParameters) -> None:
        self.params = params

    def __init_subclass__(cls) -> None:
        ALL_EXPERIMENTS[f"{cls.__module__}.{cls.__name__}"] = cls

    @classmethod
    def create(
        cls, experiment_type: str, params: Optional[Dict[str, Any]]
    ) -> "Experiment":
        experiment_klass = ALL_EXPERIMENTS[experiment_type]
        # pyre-ignore[16]: experiment_klass has no __orig_bases__ attribute
        params_klass = get_args(experiment_klass.__orig_bases__[0])[0]
        params_signature = inspect.signature(params_klass)
        typed_args = (
            {
                key: params_signature.parameters[key].annotation(value)
                for key, value in params.items()
            }
            if params
            else {}
        )
        params = params_klass(**typed_args)
        # pyre-ignore[45]: Cannot instantiate abstract class Experiment
        return experiment_klass(params)

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def measure(self) -> TOutputData:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError
