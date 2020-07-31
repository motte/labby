from unittest import TestCase
from unittest.mock import Mock

from labctl.hw.core import HardwareIOException, PSUMode
from labctl.hw.tdklambda import psu as tdklambda_psu
from labctl.tests.utils import fake_serial_port


class ZUPTest(TestCase):
    @fake_serial_port
    def test_opening_with_default_address(self, serial_port_mock: Mock) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600):
            serial_port_mock.write.assert_called_once_with(b":ADR01;")

    @fake_serial_port
    def test_opening_with_custom_address(self, serial_port_mock: Mock) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600, address=42):
            serial_port_mock.write.assert_called_once_with(b":ADR42;")

    @fake_serial_port
    def test_closes_automatically_from_with_block(self, serial_port_mock: Mock) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600):
            pass
        serial_port_mock.close.assert_called_once()

    @fake_serial_port
    def test_can_be_used_without_with_block(self, serial_port_mock: Mock) -> None:
        psu = tdklambda_psu.ZUP("/dev/ttyUSB0", 9600)
        psu.open()
        serial_port_mock.write.assert_called_once_with(b":ADR01;")
        psu.close()
        serial_port_mock.close.assert_called_once()

    @fake_serial_port
    def test_setting_target_voltage(self, serial_port_mock: Mock) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            serial_port_mock.reset_mock()
            psu.set_target_voltage(4.25)
            serial_port_mock.write.assert_called_once_with(b":VOL4.250;")

    @fake_serial_port
    def test_setting_target_current(self, serial_port_mock: Mock) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            serial_port_mock.reset_mock()
            psu.set_target_current(1.23)
            serial_port_mock.write.assert_called_once_with(b":CUR001.23;")

    @fake_serial_port
    def test_get_model(self, serial_port_mock: Mock) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            serial_port_mock.reset_mock()
            serial_port_mock.readline.return_value = b"FOOBAR\r\n"
            returned_model = psu.get_model()
            serial_port_mock.write.assert_called_once_with(b":MDL?;")
            self.assertEquals(returned_model, "FOOBAR")

    @fake_serial_port
    def test_get_software_version(self, serial_port_mock: Mock) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            serial_port_mock.reset_mock()
            serial_port_mock.readline.return_value = b"V4.2.0\r\n"
            returned_version = psu.get_software_version()
            serial_port_mock.write.assert_called_once_with(b":REV?;")
            self.assertEquals(returned_version, "V4.2.0")

    @fake_serial_port
    def test_is_output_on(self, serial_port_mock: Mock) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            serial_port_mock.reset_mock()
            serial_port_mock.readline.return_value = b"OT1\r\n"
            self.assertTrue(psu.is_output_on())
            serial_port_mock.write.assert_called_once_with(b":OUT?;")

            serial_port_mock.reset_mock()
            serial_port_mock.readline.return_value = b"OT0\r\n"
            self.assertFalse(psu.is_output_on())
            serial_port_mock.write.assert_called_once_with(b":OUT?;")

    @fake_serial_port
    def test_set_output_on(self, serial_port_mock: Mock) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            serial_port_mock.reset_mock()
            psu.set_output_on(True)
            serial_port_mock.write.assert_called_once_with(b":OUT1;")

            serial_port_mock.reset_mock()
            psu.set_output_on(False)
            serial_port_mock.write.assert_called_once_with(b":OUT0;")

    @fake_serial_port
    def test_get_target_voltage(self, serial_port_mock: Mock) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            serial_port_mock.reset_mock()
            serial_port_mock.readline.return_value = b"SV1.42\r\n"
            returned_target_voltage = psu.get_target_voltage()
            serial_port_mock.write.assert_called_once_with(b":VOL!;")
            self.assertAlmostEqual(returned_target_voltage, 1.42)

    @fake_serial_port
    def test_get_target_current(self, serial_port_mock: Mock) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            serial_port_mock.reset_mock()
            serial_port_mock.readline.return_value = b"SA0.01\r\n"
            returned_target_current = psu.get_target_current()
            serial_port_mock.write.assert_called_once_with(b":CUR!;")
            self.assertAlmostEqual(returned_target_current, 0.01)

    @fake_serial_port
    def test_get_actual_voltage(self, serial_port_mock: Mock) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            serial_port_mock.reset_mock()
            serial_port_mock.readline.return_value = b"AV1.33\r\n"
            returned_actual_voltage = psu.get_actual_voltage()
            serial_port_mock.write.assert_called_once_with(b":VOL?;")
            self.assertAlmostEqual(returned_actual_voltage, 1.33)

    @fake_serial_port
    def test_get_actual_current(self, serial_port_mock: Mock) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            serial_port_mock.reset_mock()
            serial_port_mock.readline.return_value = b"AA0.02\r\n"
            returned_actual_current = psu.get_actual_current()
            serial_port_mock.write.assert_called_once_with(b":CUR?;")
            self.assertAlmostEqual(returned_actual_current, 0.02)

    @fake_serial_port
    def test_get_mode(self, serial_port_mock: Mock) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            serial_port_mock.reset_mock()
            serial_port_mock.readline.return_value = b"OS100000000"
            returned_mode = psu.get_mode()
            serial_port_mock.write.assert_called_once_with(b":STA?;")
            self.assertEqual(returned_mode, PSUMode.CONSTANT_CURRENT)

    @fake_serial_port
    def test_invalid_response(self, serial_port_mock: Mock) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            serial_port_mock.readline.return_value = b"foobar\r\n"
            with self.assertRaisesRegex(
                HardwareIOException, "Could not parse response"
            ):
                psu.get_actual_voltage()
