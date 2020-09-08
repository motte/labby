from labby.cli.core import BaseArgumentParser, Command


class StopCommand(Command[BaseArgumentParser]):
    TRIGGER: str = "stop"

    def main(self, args: BaseArgumentParser) -> int:
        self.client.halt()
        return 0
