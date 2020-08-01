from unittest import TestCase

from labctl.config import Config
from labctl.hw import tdklambda


class ConfigTest(TestCase):
    def test_basic_config(self) -> None:
        config = Config(
            """
---
devices:
  - name: "zup-6-132"
    type: power_supply
    driver: labctl.hw.tdklambda.power_supply.ZUP
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
        self.assertEquals(device.port, "/dev/ttyUSB0")
        self.assertEquals(device.baudrate, 9600)
        self.assertEquals(device.address, 1)
