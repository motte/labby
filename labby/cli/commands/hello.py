from labby.cli.core import BaseArgumentParser, Command


class HelloCommand(Command[BaseArgumentParser]):
    TRIGGER: str = "hello"

    def main(self, args: BaseArgumentParser) -> int:
        print(self.client.hello())
        return 0
