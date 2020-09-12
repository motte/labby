from unittest import TestCase
from unittest.mock import Mock

from labby.config import Config
from labby.hw import tdklambda
from labby.tests.utils import fake_serial_port
from labby.utils import auto_discover_drivers


class ConfigTest(TestCase):
    def setUp(self) -> None:
        auto_discover_drivers()

    @fake_serial_port
    def test_basic_config(self, _serial_port_mock: Mock) -> None:
        config = Config(
            """
---
devices:
  - name: "zup-6-132"
    type: power_supply
    driver: labby.hw.tdklambda.power_supply.ZUP
    args:
      port: "/dev/ttyUSB0"
      baudrate: 9600
      address: 1
        """
        )

        devices = config.get_devices()
        self.assertEqual(len(devices), 1)
        device = config.devices[0]
        assert isinstance(device, tdklambda.power_supply.ZUP)
        self.assertEqual(device.port, "/dev/ttyUSB0")
        self.assertEqual(device.baudrate, 9600)
        self.assertEqual(device.address, 1)
