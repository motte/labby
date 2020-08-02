import os
import sys
from importlib import import_module
from pathlib import Path
from tap import Tap

from labctl.cli.core import ALL_COMMANDS, Command


# pyre-ignore[13]: command is unitialized
class ArgumentParser(Tap):
    command: str

    def add_arguments(self) -> None:
        self.add_argument("command", choices=set(ALL_COMMANDS.keys() - {"hello"}))


def _auto_discover_commands() -> None:
    COMMANDS_PATH = Path(__file__).parent / "commands"
    for f in COMMANDS_PATH.glob("*.py"):
        if "__" not in f.stem:
            import_module(f".commands.{f.stem}", __package__)


def main() -> None:
    sys.path.append(os.getcwd())
    _auto_discover_commands()

    if len(sys.argv) > 1 and Command.is_valid(sys.argv[1]):
        Command.run(sys.argv[1], sys.argv[2:])
        sys.exit(0)

    ArgumentParser().parse_args()
