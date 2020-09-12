import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Generic, Optional, Type, TypeVar, Sequence

from pyre_extensions import none_throws

from labby.config import Config
from labby.hw.core.power_supply import PowerSupply
from labby.utils.typing import get_args


@dataclass(frozen=True)
class BaseOutputData:
    @classmethod
    def get_column_names(self) -> Sequence[str]:
        # pyre-ignore[16]: pyre doesn't seem to know about __dataclass_fields__
        return list(self.__dataclass_fields__.keys())


@dataclass(frozen=True)
class BaseInputParameters:
    pass


TOutputData = TypeVar("TOutputData", bound=BaseOutputData, covariant=True)
TInputParameters = TypeVar(
    "TInputParameters", bound=BaseInputParameters, covariant=True
)


ALL_EXPERIMENTS: Dict[str, Type["Experiment[BaseInputParameters, BaseOutputData]"]] = {}


class Experiment(Generic[TInputParameters, TOutputData], ABC):
    SAMPLING_RATE_IN_HZ: float
    DURATION_IN_SECONDS: float

    name: str
    params: TInputParameters
    config: Optional[Config] = None

    def __init__(self, name: str, params: TInputParameters) -> None:
        self.name = name
        self.params = params

    def __init_subclass__(cls) -> None:
        ALL_EXPERIMENTS[f"{cls.__module__}.{cls.__name__}"] = cls

    @classmethod
    def create(
        cls, experiment_type: str, name: str, params: Optional[Dict[str, Any]]
    ) -> "Experiment[BaseInputParameters, BaseOutputData]":
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
        return experiment_klass(name, params)

    @classmethod
    def get_output_data_type(cls) -> Type[BaseOutputData]:
        # pyre-ignore[16]: cls has no __orig_bases__ attribute
        return get_args(cls.__orig_bases__[0])[1]

    def get_power_supply(self, name: str) -> PowerSupply:
        config = none_throws(self.config)
        try:
            return next(
                d
                for d in config.get_devices()
                if isinstance(d, PowerSupply) and d.name == name
            )
        except StopIteration:
            raise Exception(f"Power Supply not found: {name}")

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def measure(self) -> TOutputData:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError
