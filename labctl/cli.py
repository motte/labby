import sys
from abc import ABC, abstractmethod
from tap import Tap
from typing import Dict, Generic, Sequence, Type, TypeVar, get_args
from wasabi import color, msg

from labctl.config import Config


# pyre-ignore[13]: command is unitialized
class ArgumentParser(Tap):
    command: str

    def add_arguments(self) -> None:
        self.add_argument("command")


class BaseArgumentParser(Tap):
    config: str = "labctl.yml"


TArgumentParser = TypeVar("TArgumentParser", bound=BaseArgumentParser)


ALL_COMMANDS: Dict[str, Type["Command"]] = {}


class Command(Generic[TArgumentParser], ABC):
    TRIGGER: str
    config: Config

    def __init__(self, config: Config) -> None:
        self.config = config

    def __init_subclass__(cls) -> None:
        ALL_COMMANDS[f"{cls.TRIGGER}"] = cls

    @classmethod
    def run(cls, trigger: str, argv: Sequence[str]) -> None:
        command_klass = ALL_COMMANDS[trigger]
        # pyre-ignore[16]: command_klass has no __orig_bases__ attribute
        args_klass = get_args(command_klass.__orig_bases__[0])[0]
        args = args_klass().parse_args(argv)

        with open(args.config, "r") as config_file:
            config = Config(config_file.read())

        # pyre-ignore[45]: cannot instantiate Command with abstract method
        command = command_klass(config)
        command.main(args)

    @abstractmethod
    def main(self, args: TArgumentParser) -> None:
        raise NotImplementedError


class HelloCommand(Command[BaseArgumentParser]):
    TRIGGER: str = "hello"

    def main(self, args: BaseArgumentParser) -> None:
        print("Hello world")


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


def main() -> None:
    # FIXME: labctl devices --help isn't showing the right help message
    args = ArgumentParser().parse_args()

    if args.command not in ALL_COMMANDS.keys():
        print(f"Error: Invalid command {args.command}\n")
        args.print_help()
        sys.exit(2)

    Command.run(args.command, sys.argv[2:])
    sys.exit(0)
