import sys
from tap import Tap

# import all commands
import labctl.cli.commands  # noqa: F401

from labctl.cli.core import Command


# pyre-ignore[13]: command is unitialized
class ArgumentParser(Tap):
    command: str

    def add_arguments(self) -> None:
        self.add_argument("command")


def main() -> None:
    if len(sys.argv) > 1 and Command.is_valid(sys.argv[1]):
        Command.run(sys.argv[1], sys.argv[2:])
        sys.exit(0)

    args = ArgumentParser().parse_args()
    print(f"Error: Invalid command {args.command}\n")
    args.print_help()
    sys.exit(2)
