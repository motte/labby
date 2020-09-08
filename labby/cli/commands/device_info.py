from typing import List, Tuple

from pyre_extensions import none_throws
from wasabi import color, msg, Printer

from labby.cli.core import BaseArgumentParser, Command
from labby.hw.core import DeviceType
from labby.hw.core.power_supply import PowerSupplyMode
from labby.server import DeviceInfoResponse, PowerSupplyInfo


render = Printer(no_print=True)


# pyre-ignore[13]: device_name is unitialized
class DeviceInfoArguments(BaseArgumentParser):
    device_name: str

    def add_arguments(self) -> None:
        self.add_argument("device_name")


class DeviceInfoCommand(Command[DeviceInfoArguments]):
    TRIGGER: str = "device-info"

    def _get_power_supply_info(
        self, power_supply: PowerSupplyInfo
    ) -> List[Tuple[str, str]]:
        info: List[Tuple[str, str]] = []

        info.append(
            (
                "Status",
                render.text("● ON", color="green")
                if power_supply.is_output_on
                else render.text("● OFF", color="grey"),
            )
        )

        info.append(
            (
                "Mode",
                "Constant Current"
                if power_supply.mode == PowerSupplyMode.CONSTANT_CURRENT
                else "Constant Voltage",
            )
        )

        info.append(("Target Voltage", f"{power_supply.target_voltage:.2f}V"))
        info.append(("Actual Voltage", f"{power_supply.actual_voltage:.2f}V"))

        info.append(("Target Current", f"{power_supply.target_current:.2f}A"))
        info.append(("Actual Current", f"{power_supply.actual_current:.2f}A"))

        return info

    def _render_device_info(self, device: DeviceInfoResponse) -> List[Tuple[str, str]]:
        if device.device_type == DeviceType.POWER_SUPPLY:
            return self._get_power_supply_info(none_throws(device.power_supply_info))
        raise Exception(f"Unknown device type {type(device)}")

    def main(self, args: DeviceInfoArguments) -> int:
        device_info = self.client.device_info(args.device_name)
        if device_info.device_type is None:
            msg.fail(
                f"Unknown device {args.device_name}",
                text="See `labby devices` for a list of available devices.",
            )
            return 1

        msg.divider(f"{args.device_name} (device_info.device_type.friendly_name)")

        if device_info.is_connected:
            msg.table(
                [
                    ("Connection", render.good("OK")),
                    *self._render_device_info(device_info),
                ]
            )
        else:
            msg.table([("Connection", render.fail("Error"))])
            msg.text(
                f"{color(device_info.error_type, bold=True)}: "
                + f"{device_info.error_message}"
            )

        return 0
