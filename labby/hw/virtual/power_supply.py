import math

from labby.hw.core.power_supply import (
    PowerSupply as BasePowerSupply,
    PowerSupplyMode,
)


class PowerSupply(BasePowerSupply):
    is_on: bool = False
    load_in_ohms: float
    target_current: float = 0.0
    target_voltage: float = 0.0

    def __init__(self, load_in_ohms: float) -> None:
        self.load_in_ohms = load_in_ohms

    def get_mode(self) -> PowerSupplyMode:
        return (
            PowerSupplyMode.CONSTANT_VOLTAGE
            if math.isclose(self.get_actual_voltage(), self.target_voltage)
            else PowerSupplyMode.CONSTANT_CURRENT
        )

    def get_actual_voltage(self) -> float:
        return self.get_actual_current() * self.load_in_ohms

    def get_actual_current(self) -> float:
        if not self.is_on:
            return 0.0
        return min(self.target_voltage / self.load_in_ohms, self.target_current)

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass

    def test_connection(self) -> None:
        pass

    def is_output_on(self) -> bool:
        return self.is_on

    def set_output_on(self, is_on: bool) -> None:
        self.is_on = is_on

    def get_target_voltage(self) -> float:
        return self.target_voltage

    def get_target_current(self) -> float:
        return self.target_current

    def set_target_voltage(self, voltage: float) -> None:
        self.target_voltage = voltage

    def set_target_current(self, current: float) -> None:
        self.target_current = current


class BrokenPowerSupply(PowerSupply):
    def test_connection(self) -> None:
        raise Exception("Unavailable device")
