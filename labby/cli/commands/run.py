from labby.cli.core import BaseArgumentParser, Command


# pyre-ignore[13]: sequence_filename is unitialized
class RunArgumentParser(BaseArgumentParser):
    sequence_filename: str

    def add_arguments(self) -> None:
        self.add_argument("sequence_filename")


class RunCommand(Command[RunArgumentParser]):
    TRIGGER: str = "run"

    def main(self, args: RunArgumentParser) -> int:
        self.get_client().run_sequence(args.sequence_filename)
        return 0
