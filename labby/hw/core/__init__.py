import inspect
from abc import ABC, abstractmethod
from enum import Enum
from types import TracebackType
from typing import Any, Dict, Optional, Type


ALL_DRIVERS: Dict[str, Type["Device"]] = {}


class DeviceType(Enum):
    POWER_SUPPLY = "POWER_SUPPLY"

    @property
    def friendly_name(self) -> str:
        if self == DeviceType.POWER_SUPPLY:
            return "Power Supply"
        raise NotImplementedError


class Device(ABC):
    name: str = "unnamed device"
    device_type: DeviceType

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
