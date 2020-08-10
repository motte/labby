from unittest import TestCase
from unittest.mock import Mock

from serial import SerialException

from labby.hw.core.power_supply import (
    PowerSupply,
    PowerSupplyMode,
)
from labby.hw.core.serial import SerialDevice
from labby.tests.utils import fake_serial_port


class TestSerialPowerSupply(SerialDevice, PowerSupply):
    def __init__(self, port: str, baudrate: int) -> None:
        SerialDevice.__init__(self, port, baudrate)

    def test_connection(self) -> None:
        return

    def get_mode(self) -> PowerSupplyMode:
        raise NotImplementedError

    def is_output_on(self) -> bool:
        raise NotImplementedError

    def set_output_on(self, is_on: bool) -> None:
        raise NotImplementedError

    def get_target_voltage(self) -> float:
        raise NotImplementedError

    def get_actual_voltage(self) -> float:
        raise NotImplementedError

    def get_target_current(self) -> float:
        raise NotImplementedError

    def get_actual_current(self) -> float:
        raise NotImplementedError

    def set_target_voltage(self, voltage: float) -> None:
        raise NotImplementedError

    def set_target_current(self, current: float) -> None:
        raise NotImplementedError


class SerialDeviceTest(TestCase):
    @fake_serial_port
    def test_fail_to_open_serial_port(self, serial_port_mock: Mock) -> None:
        serial_port_mock.is_open = False
        serial_port_mock.open.side_effect = SerialException("Cannot open serial port")
        with self.assertRaises(SerialException):
            with TestSerialPowerSupply("/dev/ttyUSB0", 9600):
                pass
