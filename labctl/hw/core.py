from abc import ABC
from enum import Enum


class PSUMode(Enum):
    CONSTANT_VOLTAGE = 0
    CONSTANT_CURRENT = 1


class PSU(ABC):
    pass
