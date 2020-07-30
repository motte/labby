from tap import Tap


class ArgumentParser(Tap):
    hello: bool = False


def main() -> None:
    args = ArgumentParser().parse_args()
    if args.hello:
        print("Hello world")
