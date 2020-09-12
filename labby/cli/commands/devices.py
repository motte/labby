from wasabi import color, msg

from labby.cli.core import BaseArgumentParser, Command


class DevicesCommand(Command[BaseArgumentParser]):
    TRIGGER: str = "devices"

    def main(self, args: BaseArgumentParser) -> int:
        list_devices_response = self.get_client().list_devices()
        msg.divider("Registered Devices")
        for device in list_devices_response.devices:
            if device.is_available:
                msg.good(f"{device.name}")
            else:
                msg.fail(f"{device.name}:")
                msg.text(
                    f"  {color(device.error_type, bold=True)}: {device.error_message}"
                )
        return 0
