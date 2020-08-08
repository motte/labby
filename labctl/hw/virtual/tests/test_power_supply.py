from unittest import TestCase

from labctl.hw.virtual.power_supply import (
    BrokenPowerSupply,
    PowerSupply,
    PowerSupplyMode,
)


class PowerSupplyTest(TestCase):
    def test_power_supply_initial_state(self) -> None:
        power_supply = PowerSupply(42)
        power_supply.test_connection()
        self.assertEquals(power_supply.is_output_on(), False)
        self.assertAlmostEquals(power_supply.get_target_current(), 0)
        self.assertAlmostEquals(power_supply.get_target_voltage(), 0)
        self.assertAlmostEquals(power_supply.get_actual_current(), 0)
        self.assertAlmostEquals(power_supply.get_actual_voltage(), 0)
        self.assertEquals(power_supply.get_mode(), PowerSupplyMode.CONSTANT_VOLTAGE)

    def test_power_supply_load(self) -> None:
        power_supply = PowerSupply(4)
        power_supply.set_target_voltage(8)
        power_supply.set_target_current(3)
        power_supply.set_output_on(True)
        self.assertAlmostEquals(power_supply.get_actual_current(), 2)
        self.assertAlmostEquals(power_supply.get_actual_voltage(), 8)
        self.assertEquals(power_supply.get_mode(), PowerSupplyMode.CONSTANT_VOLTAGE)

        power_supply = PowerSupply(2)
        power_supply.set_target_voltage(8)
        power_supply.set_target_current(3)
        power_supply.set_output_on(True)
        self.assertAlmostEquals(power_supply.get_actual_current(), 3)
        self.assertAlmostEquals(power_supply.get_actual_voltage(), 6)
        self.assertEquals(power_supply.get_mode(), PowerSupplyMode.CONSTANT_CURRENT)

        power_supply = PowerSupply(5)
        power_supply.set_target_voltage(15)
        power_supply.set_target_current(4)
        power_supply.set_output_on(True)
        self.assertAlmostEquals(power_supply.get_actual_current(), 3)
        self.assertAlmostEquals(power_supply.get_actual_voltage(), 15)
        self.assertEquals(power_supply.get_mode(), PowerSupplyMode.CONSTANT_VOLTAGE)

        power_supply = PowerSupply(3)
        power_supply.set_target_voltage(15)
        power_supply.set_target_current(4)
        power_supply.set_output_on(True)
        self.assertAlmostEquals(power_supply.get_actual_current(), 4)
        self.assertAlmostEquals(power_supply.get_actual_voltage(), 12)
        self.assertEquals(power_supply.get_mode(), PowerSupplyMode.CONSTANT_CURRENT)

    def test_power_supply_when_output_is_off(self) -> None:
        power_supply = PowerSupply(4)
        power_supply.set_target_voltage(8)
        power_supply.set_target_current(3)
        self.assertAlmostEquals(power_supply.get_actual_current(), 0.0)
        self.assertAlmostEquals(power_supply.get_actual_voltage(), 0.0)


class BrokenPowerSupplyTest(TestCase):
    def test_power_supply_initial_state(self) -> None:
        power_supply = BrokenPowerSupply(42)
        with self.assertRaises(Exception):
            power_supply.test_connection()
