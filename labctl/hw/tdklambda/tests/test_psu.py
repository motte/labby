from unittest import TestCase
from unittest.mock import _patch, patch, Mock

from labctl.hw.tdklambda import psu as tdklambda_psu


SERIAL_PORT_MOCK = Mock()


@patch("labctl.hw.tdklambda.psu.fcntl.flock", Mock())
class ZUPTest(TestCase):
    serial_port_mock: Mock
    serial_port_patch: _patch

    def setUp(self) -> None:
        self.serial_port_mock = Mock()
        self.serial_port_patch = patch(
            "labctl.hw.tdklambda.psu.Serial", return_value=self.serial_port_mock,
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
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600, address=42) as psu:
            self.serial_port_mock.reset_mock()
            psu.set_target_voltage(4.25)
            self.serial_port_mock.write.assert_called_once_with(b":VOL4.250;")

    def test_setting_target_current(self) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600, address=42) as psu:
            self.serial_port_mock.reset_mock()
            psu.set_target_current(1.23)
            self.serial_port_mock.write.assert_called_once_with(b":CUR001.23;")

    def test_get_model(self) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600, address=42) as psu:
            self.serial_port_mock.reset_mock()
            self.serial_port_mock.readline.return_value = b"FOOBAR\r\n"
            returned_model = psu.get_model()
            self.serial_port_mock.write.assert_called_once_with(b":MDL?;")
            self.assertEquals(returned_model, "FOOBAR")

    def test_is_output_on(self) -> None:
        with tdklambda_psu.ZUP("/dev/ttyUSB0", 9600, address=42) as psu:
            self.serial_port_mock.reset_mock()
            self.serial_port_mock.readline.return_value = b"OT1\r\n"
            self.assertTrue(psu.is_output_on())
            self.serial_port_mock.write.assert_called_once_with(b":OUT?;")

            self.serial_port_mock.reset_mock()
            self.serial_port_mock.readline.return_value = b"OT0\r\n"
            self.assertFalse(psu.is_output_on())
            self.serial_port_mock.write.assert_called_once_with(b":OUT?;")
