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

    def add_arguments(self) -> None:
        self.add_argument("command")


def list_devices(config: Config) -> None:
    print("Available Devices:")
    for device in config.devices:
        print(f"● {device.__class__}")


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

    with open("labctl.yml", "r") as config_file:
        config = Config(config_file.read())

    if command == Command.DEVICES:
        list_devices(config)
        sys.exit(0)
