from wasabi import color, msg

from labctl.cli.core import BaseArgumentParser, Command


class DevicesCommand(Command[BaseArgumentParser]):
    TRIGGER: str = "devices"

    def main(self, args: BaseArgumentParser) -> None:
        msg.divider("Registered Devices")
        for device in self.config.devices:
            try:
                device.open()
                device.test_connection()
                msg.good(f"{device.name}")
            except Exception as ex:
                msg.fail(f"{device.name}:")
                msg.text(f"  {color(type(ex).__name__, bold=True)}: {str(ex)}")
            finally:
                device.close()
