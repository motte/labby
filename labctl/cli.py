from tap import Tap


class ArgumentParser(Tap):
    command: str = "help"

    def add_arguments(self) -> None:
        self.add_argument("command")


def main() -> None:
    args = ArgumentParser().parse_args()
    if args.command == "help":
        args.print_help()
        return

    print("Hello world")
