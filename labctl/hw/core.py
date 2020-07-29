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
    def is_output_on(self) -> bool:
        ...

    @abstractmethod
    def set_output_on(self, is_on: bool) -> None:
        ...

    @abstractmethod
    def get_target_voltage(self) -> float:
        ...

    @abstractmethod
    def get_actual_voltage(self) -> float:
        ...

    @abstractmethod
    def get_target_current(self) -> float:
        ...

    @abstractmethod
    def get_actual_current(self) -> float:
        ...

    @abstractmethod
    def set_target_voltage(self, voltage: float) -> None:
        ...

    @abstractmethod
    def set_target_current(self, current: float) -> None:
        ...


class HardwareIOException(Exception):
    pass
