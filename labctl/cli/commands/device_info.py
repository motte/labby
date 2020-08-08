from typing import List, Tuple

from wasabi import color, msg, Printer

from labctl.hw.core import Device, PowerSupply, PowerSupplyMode
from labctl.cli.core import BaseArgumentParser, Command


render = Printer(no_print=True)


# pyre-ignore[13]: device_name is unitialized
class DeviceInfoArguments(BaseArgumentParser):
    device_name: str

    def add_arguments(self) -> None:
        self.add_argument("device_name")


class DeviceInfoCommand(Command[DeviceInfoArguments]):
    TRIGGER: str = "device-info"

    def _get_power_supply_info(
        self, power_supply: PowerSupply
    ) -> List[Tuple[str, str]]:
        info: List[Tuple[str, str]] = []

        info.append(
            (
                "Status",
                render.text("● ON", color="green")
                if power_supply.is_output_on()
                else render.text("● OFF", color="grey"),
            )
        )

        info.append(
            (
                "Mode",
                "Constant Current"
                if power_supply.get_mode() == PowerSupplyMode.CONSTANT_CURRENT
                else "Constant Voltage",
            )
        )

        info.append(("Target Voltage", f"{power_supply.get_target_voltage():.2f}V"))
        info.append(("Actual Voltage", f"{power_supply.get_actual_voltage():.2f}V"))

        info.append(("Target Current", f"{power_supply.get_target_current():.2f}A"))
        info.append(("Actual Current", f"{power_supply.get_actual_current():.2f}A"))

        return info

    def _render_device_info(self, device: Device) -> List[Tuple[str, str]]:
        if isinstance(device, PowerSupply):
            return self._get_power_supply_info(device)
        raise Exception(f"Unknown device type {type(device)}")

    def main(self, args: DeviceInfoArguments) -> None:
        try:
            device = next(
                device
                for device in self.config.devices
                if device.name == args.device_name
            )
        except StopIteration:
            msg.fail(
                f"Unknown device {args.device_name}",
                text="See `labctl devices` for a list of available devices.",
            )
            return

        msg.divider(f"{device.name} (Power Supply)")

        try:
            device.open()
            device.test_connection()

            msg.table(
                [("Connection", render.good("OK")), *self._render_device_info(device)]
            )
        except Exception as ex:
            msg.table([("Connection", render.fail("Error"))])
            msg.text(f"{color(type(ex).__name__, bold=True)}: {str(ex)}")
        finally:
            device.close()
