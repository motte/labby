from unittest import TestCase
from unittest.mock import Mock

from serial import SerialException, SerialTimeoutException

from labby.hw.core.power_supply import (
    PowerSupply,
    PowerSupplyMode,
)
from labby.hw.core.serial import SerialDevice, SERIAL_CONTROLLERS
from labby.tests.utils import fake_serial_port


class TestSerialPowerSupply(SerialDevice, PowerSupply):
    def __init__(self, port: str, baudrate: int) -> None:
        SerialDevice.__init__(self, port, baudrate)

    def test_connection(self) -> None:
        return

    def get_mode(self) -> PowerSupplyMode:
        return PowerSupplyMode(int(self._query(b":mode?")))

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

    @fake_serial_port
    def test_write_timeout(self, serial_port_mock: Mock) -> None:
        serial_port_mock.write.side_effect = SerialTimeoutException("Timeout")
        with self.assertRaises(SerialTimeoutException):
            with TestSerialPowerSupply("/dev/ttyUSB1", 9600) as power_supply:
                power_supply.get_mode()

    @fake_serial_port
    def test_successful_write_and_read(self, serial_port_mock: Mock) -> None:
        serial_port_mock.readline.return_value = b"0\r\n"
        with TestSerialPowerSupply("/dev/ttyUSB1", 9600) as power_supply:
            self.assertEquals(power_supply.get_mode(), PowerSupplyMode.CONSTANT_VOLTAGE)


class SerialControllerTest(TestCase):
    @fake_serial_port
    def test_serial_controllers_are_purged_on_close(
        self, _serial_port_mock: Mock
    ) -> None:
        self.assertEquals(len(SERIAL_CONTROLLERS), 0)
        with TestSerialPowerSupply("/dev/ttyUSB0", 9600):
            self.assertEquals(len(SERIAL_CONTROLLERS), 1)
            self.assertIn("/dev/ttyUSB0", SERIAL_CONTROLLERS.keys())
        self.assertEquals(len(SERIAL_CONTROLLERS), 0)
