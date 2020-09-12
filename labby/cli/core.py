from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Generic, Sequence, Type, TypeVar

from tap import Tap

from labby.client import Client
from labby.config import Config
from labby.server import DEFAULT_ADDRESS
from labby.utils import auto_discover_drivers
from labby.utils.typing import get_args


class BaseArgumentParser(Tap):
    config: str = "labby.yml"


TArgumentParser = TypeVar("TArgumentParser", bound=BaseArgumentParser)


ALL_COMMANDS: Dict[str, Type[Command[BaseArgumentParser]]] = {}


class Command(Generic[TArgumentParser], ABC):
    TRIGGER: str
    config: Config

    def __init__(self, config: Config) -> None:
        self.config = config

    def __init_subclass__(cls: Type[Command[BaseArgumentParser]]) -> None:
        ALL_COMMANDS[f"{cls.TRIGGER}"] = cls

    def get_client(self) -> Client:
        return Client(DEFAULT_ADDRESS)

    @classmethod
    def run(cls, trigger: str, argv: Sequence[str]) -> int:
        command_klass = ALL_COMMANDS[trigger]
        # pyre-ignore[16]: command_klass has no __orig_bases__ attribute
        args_klass = get_args(command_klass.__orig_bases__[0])[0]
        args = args_klass(prog=f"labby {trigger}").parse_args(argv)

        auto_discover_drivers()
        with open(args.config, "r") as config_file:
            config = Config(config_file.read())

        # pyre-ignore[45]: cannot instantiate Command with abstract method
        command = command_klass(config)
        return command.main(args)

    @classmethod
    def is_valid(cls, trigger: str) -> bool:
        return trigger in ALL_COMMANDS.keys()

    @abstractmethod
    def main(self, args: TArgumentParser) -> int:
        raise NotImplementedError
