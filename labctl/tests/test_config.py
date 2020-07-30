import strictyaml
from unittest import TestCase

from labctl.config import Config


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
      baud_rate: 9600
      address: 1
        """
        )

        self.assertEqual(len(config.config["devices"]), 1)
