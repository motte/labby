from unittest import TestCase
from labby.hw.core import DeviceType


class DeviceTypeTest(TestCase):
    def test_all_device_types_have_a_friendly_name(self) -> None:
        for device_type in DeviceType:
            friendly_name = device_type.friendly_name
            self.assertIsInstance(friendly_name, str)
            self.assertGreater(len(friendly_name), 0)
