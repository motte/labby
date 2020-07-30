from tap import Tap


# pyre-ignore[13]: command is unitialized
class ArgumentParser(Tap):
    command: str

    def add_arguments(self) -> None:
        self.add_argument("command")


def main() -> None:
    args = ArgumentParser().parse_args()
    if args.command == "hello":
        print("Hello world")
        return
