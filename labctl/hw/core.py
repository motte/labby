from abc import ABC, abstractmethod
from enum import Enum


class PSUMode(Enum):
    CONSTANT_VOLTAGE = 0
    CONSTANT_CURRENT = 1


class PSU(ABC):
    @abstractmethod
    def get_mode(self) -> PSUMode:
        ...

    @abstractmethod
    def open(self) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...

    @abstractmethod
    def get_set_voltage(self) -> float:
        ...

    @abstractmethod
    def get_actual_voltage(self) -> float:
        ...

    @abstractmethod
    def get_set_current(self) -> float:
        ...

    @abstractmethod
    def get_actual_current(self) -> float:
        ...

    @abstractmethod
    def set_voltage(self, voltage: float) -> None:
        ...

    @abstractmethod
    def set_current(self, current: float) -> None:
        ...


class TDKLambdaException(Exception):
    pass
