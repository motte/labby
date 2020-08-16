from abc import ABC, abstractmethod
from enum import Enum

from labby.hw.core import Device, DeviceType


class PowerSupplyMode(Enum):
    CONSTANT_VOLTAGE = 0
    CONSTANT_CURRENT = 1


class PowerSupply(Device, ABC):
    device_type: DeviceType = DeviceType.POWER_SUPPLY

    def __enter__(self) -> "PowerSupply":
        Device.__enter__(self)
        return self

    @abstractmethod
    def get_mode(self) -> PowerSupplyMode:
        raise NotImplementedError

    @abstractmethod
    def is_output_on(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def set_output_on(self, is_on: bool) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_target_voltage(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def get_actual_voltage(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def get_target_current(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def get_actual_current(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def set_target_voltage(self, voltage: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_target_current(self, current: float) -> None:
        raise NotImplementedError
