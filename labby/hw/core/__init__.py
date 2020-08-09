import inspect
from abc import ABC, abstractmethod
from enum import Enum
from importlib import import_module
from pathlib import Path
from types import TracebackType
from typing import Any, Dict, Optional, Type


class PowerSupplyMode(Enum):
    CONSTANT_VOLTAGE = 0
    CONSTANT_CURRENT = 1


ALL_DRIVERS: Dict[str, Type["Device"]] = {}


class Device(ABC):
    name: str = "unnamed device"

    def __init_subclass__(cls) -> None:
        ALL_DRIVERS[f"{cls.__module__}.{cls.__name__}"] = cls

    @abstractmethod
    def open(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    def __enter__(self) -> "Device":
        self.open()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        self.close()
        return False

    @abstractmethod
    def test_connection(self) -> None:
        raise NotImplementedError

    @classmethod
    def create(cls, name: str, driver: str, args: Dict[str, Any]) -> "Device":
        klass = ALL_DRIVERS[driver]
        signature = inspect.signature(klass)
        typed_args = {
            key: signature.parameters[key].annotation(value)
            for key, value in args.items()
        }
        # pyre-ignore[45]: Cannot instantiate abstract class Device
        device = klass(**typed_args)
        device.name = name
        return device


class PowerSupply(Device, ABC):
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


class HardwareIOException(Exception):
    pass


def auto_discover_drivers() -> None:
    HW_PATH = Path(__file__).parent.parent
    for f in HW_PATH.glob("**/*.py"):
        if "__" in f.stem or "test" in f.stem or f.parent.stem == "hw":
            continue
        import_module(f"labby.hw.{f.parent.stem}.{f.stem}", __package__)
