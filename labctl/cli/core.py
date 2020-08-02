from abc import ABC, abstractmethod
from tap import Tap
from typing import Dict, Generic, Sequence, Type, TypeVar, get_args

from labctl.config import Config
from labctl.hw.core import auto_discover_drivers


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
        args = args_klass(prog=f"labctl {trigger}").parse_args(argv)

        auto_discover_drivers()
        with open(args.config, "r") as config_file:
            config = Config(config_file.read())

        # pyre-ignore[45]: cannot instantiate Command with abstract method
        command = command_klass(config)
        command.main(args)

    @classmethod
    def is_valid(cls, trigger: str) -> bool:
        return trigger in ALL_COMMANDS.keys()

    @abstractmethod
    def main(self, args: TArgumentParser) -> None:
        raise NotImplementedError


def auto_discover_experiments() -> None:
    from importlib import import_module
    from pathlib import Path

    COMMANDS_PATH = Path("./experiments")
    for f in COMMANDS_PATH.glob("*.py"):
        if "__" not in f.stem:
            import_module(f"experiments.{f.stem}", __package__)
