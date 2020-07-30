import strictyaml
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
    type: psu
    driver: labctl.hw.tdklambda.psu.ZUP
    args:
      port: "/dev/ttyUSB0"
      baudrate: 9600
      address: 1
        """
        )

        devices = config.get_devices()
        self.assertEqual(len(devices), 1)
        device = config.devices[0]
        assert isinstance(device, tdklambda.psu.ZUP)
        self.assertEquals(device.port, "/dev/ttyUSB0")
        # FIXME: these should be integers
        self.assertEquals(device.baudrate, "9600")
        self.assertEquals(device.address, "1")
