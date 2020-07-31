from unittest import TestCase
from unittest.mock import _patch, patch, Mock

from labctl.hw.core import HardwareIOException, PSUMode
from labctl.hw.tdklambda import psu as tdklambda_psu


SERIAL_PORT_MOCK = Mock()


@patch("labctl.hw.tdklambda.psu.fcntl.flock", Mock())
class ZUPTest(TestCase):
    serial_port_mock: Mock
    serial_port_patch: _patch

    def setUp(self) -> None:
        self.serial_port_mock = Mock()
        self.serial_port_patch = patch(
            "labctl.hw.core.Serial", return_value=self.serial_port_mock,
        )
        self.serial_port_patch.start()

    def tearDown(self) -> None:
        self.serial_port_patch.stop()

    def test_opening_with_default_address(self) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600):
            self.serial_port_mock.write.assert_called_once_with(b":ADR01;")

    def test_opening_with_custom_address(self) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600, address=42):
            self.serial_port_mock.write.assert_called_once_with(b":ADR42;")

    def test_closes_automatically_from_with_block(self) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600):
            pass
        self.serial_port_mock.close.assert_called_once()

    def test_can_be_used_without_with_block(self) -> None:
        psu = tdklambda_psu.ZUP("/dev/ttyUSB0", 9600)
        psu.open()
        self.serial_port_mock.write.assert_called_once_with(b":ADR01;")
        psu.close()
        self.serial_port_mock.close.assert_called_once()

    def test_setting_target_voltage(self) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            self.serial_port_mock.reset_mock()
            psu.set_target_voltage(4.25)
            self.serial_port_mock.write.assert_called_once_with(b":VOL4.250;")

    def test_setting_target_current(self) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            self.serial_port_mock.reset_mock()
            psu.set_target_current(1.23)
            self.serial_port_mock.write.assert_called_once_with(b":CUR001.23;")

    def test_get_model(self) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            self.serial_port_mock.reset_mock()
            self.serial_port_mock.readline.return_value = b"FOOBAR\r\n"
            returned_model = psu.get_model()
            self.serial_port_mock.write.assert_called_once_with(b":MDL?;")
            self.assertEquals(returned_model, "FOOBAR")

    def test_get_software_version(self) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            self.serial_port_mock.reset_mock()
            self.serial_port_mock.readline.return_value = b"V4.2.0\r\n"
            returned_version = psu.get_software_version()
            self.serial_port_mock.write.assert_called_once_with(b":REV?;")
            self.assertEquals(returned_version, "V4.2.0")

    def test_is_output_on(self) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            self.serial_port_mock.reset_mock()
            self.serial_port_mock.readline.return_value = b"OT1\r\n"
            self.assertTrue(psu.is_output_on())
            self.serial_port_mock.write.assert_called_once_with(b":OUT?;")

            self.serial_port_mock.reset_mock()
            self.serial_port_mock.readline.return_value = b"OT0\r\n"
            self.assertFalse(psu.is_output_on())
            self.serial_port_mock.write.assert_called_once_with(b":OUT?;")

    def test_set_output_on(self) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            self.serial_port_mock.reset_mock()
            psu.set_output_on(True)
            self.serial_port_mock.write.assert_called_once_with(b":OUT1;")

            self.serial_port_mock.reset_mock()
            psu.set_output_on(False)
            self.serial_port_mock.write.assert_called_once_with(b":OUT0;")

    def test_get_target_voltage(self) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            self.serial_port_mock.reset_mock()
            self.serial_port_mock.readline.return_value = b"SV1.42\r\n"
            returned_target_voltage = psu.get_target_voltage()
            self.serial_port_mock.write.assert_called_once_with(b":VOL!;")
            self.assertAlmostEqual(returned_target_voltage, 1.42)

    def test_get_target_current(self) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            self.serial_port_mock.reset_mock()
            self.serial_port_mock.readline.return_value = b"SA0.01\r\n"
            returned_target_current = psu.get_target_current()
            self.serial_port_mock.write.assert_called_once_with(b":CUR!;")
            self.assertAlmostEqual(returned_target_current, 0.01)

    def test_get_actual_voltage(self) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            self.serial_port_mock.reset_mock()
            self.serial_port_mock.readline.return_value = b"AV1.33\r\n"
            returned_actual_voltage = psu.get_actual_voltage()
            self.serial_port_mock.write.assert_called_once_with(b":VOL?;")
            self.assertAlmostEqual(returned_actual_voltage, 1.33)

    def test_get_actual_current(self) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            self.serial_port_mock.reset_mock()
            self.serial_port_mock.readline.return_value = b"AA0.02\r\n"
            returned_actual_current = psu.get_actual_current()
            self.serial_port_mock.write.assert_called_once_with(b":CUR?;")
            self.assertAlmostEqual(returned_actual_current, 0.02)

    def test_get_mode(self) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            self.serial_port_mock.reset_mock()
            self.serial_port_mock.readline.return_value = b"OS100000000"
            returned_mode = psu.get_mode()
            self.serial_port_mock.write.assert_called_once_with(b":STA?;")
            self.assertEqual(returned_mode, PSUMode.CONSTANT_CURRENT)

    def test_invalid_response(self) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600) as psu:
            self.serial_port_mock.readline.return_value = b"foobar\r\n"
            with self.assertRaisesRegex(
                HardwareIOException, "Could not parse response"
            ):
                psu.get_actual_voltage()
