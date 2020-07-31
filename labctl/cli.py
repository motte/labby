import sys
from enum import Enum
from tap import Tap

from labctl.config import Config


class Command(Enum):
    HELLO = "hello"
    DEVICES = "devices"


# pyre-ignore[13]: command is unitialized
class ArgumentParser(Tap):
    command: str
    config: str = "labctl.yml"

    def add_arguments(self) -> None:
        self.add_argument("command")


def list_devices(config: Config) -> None:
    print("Registered Devices:")
    for device in config.devices:
        try:
            device.open()
            device.test_connection()
            print(f"● {device.name}")
        except Exception as ex:
            print(f"  {device.name}: {type(ex).__name__}:")
            print(f"    {str(ex)}")
        finally:
            device.close()


def main() -> None:
    args = ArgumentParser().parse_args()
    try:
        command = Command(args.command)
    except ValueError:
        print(f"Error: Invalid command {args.command}\n")
        args.print_help()
        sys.exit(2)

    if command == Command.HELLO:
        print("Hello world")
        return

    with open(args.config, "r") as config_file:
        config = Config(config_file.read())

    if command == Command.DEVICES:
        list_devices(config)
        sys.exit(0)
