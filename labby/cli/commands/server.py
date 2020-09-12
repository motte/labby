from wasabi import msg
from pynng.exceptions import Timeout

from labby.cli.core import BaseArgumentParser, Command
from labby.server import Server


# pyre-ignore[13]: sequence_filename is unitialized
class ServerArgumentParser(BaseArgumentParser):
    command: str

    def add_arguments(self) -> None:
        self.add_argument("command", choices={"start", "status", "stop"})


class ServerCommand(Command[ServerArgumentParser]):
    TRIGGER: str = "server"

    def main(self, args: ServerArgumentParser) -> int:
        if args.command == "start":
            server = Server(self.config)
            server.start()
            return 0

        if args.command == "status":
            try:
                response = self.get_client().hello()
                if response == "Hello world":
                    msg.good("Active")
                    return 0
            except Timeout:
                msg.fail("Timeout")
                msg.text(
                    "The labby server did not respond. Are you sure it is started?"
                )
            return 1

        if args.command == "stop":
            self.get_client().halt()
            return 0

        raise Exception(f"Unknown server command {args.command}")
