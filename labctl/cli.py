import sys
from enum import Enum
from tap import Tap


class Command(Enum):
    HELLO = "hello"


# pyre-ignore[13]: command is unitialized
class ArgumentParser(Tap):
    command: str

    def add_arguments(self) -> None:
        self.add_argument("command")


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
