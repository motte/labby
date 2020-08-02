from labctl.cli.core import BaseArgumentParser, Command


class HelloCommand(Command[BaseArgumentParser]):
    TRIGGER: str = "hello"

    def main(self, args: BaseArgumentParser) -> None:
        print("Hello world")
