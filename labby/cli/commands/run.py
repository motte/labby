from importlib import import_module
from pathlib import Path

import wasabi
from pynng import Sub0

from labby.cli.core import BaseArgumentParser, Command
from labby.experiment.runner import (
    ExperimentRunner,
    ExperimentSequenceStatus,
    ExperimentState,
)
from labby.experiment.sequence import ExperimentSequence


# pyre-ignore[13]: sequence_filename is unitialized
class RunArgumentParser(BaseArgumentParser):
    sequence_filename: str

    def add_arguments(self) -> None:
        self.add_argument("sequence_filename")


class RunCommand(Command[RunArgumentParser]):
    TRIGGER: str = "run"

    def _auto_discover_experiments(self) -> None:
        EXPERIMENTS_PATH = Path("./experiments")
        for f in EXPERIMENTS_PATH.glob("*.py"):
            if "__" not in f.stem:
                import_module(f"experiments.{f.stem}", __package__)

    def main(self, args: RunArgumentParser) -> int:
        self._auto_discover_experiments()

        with open(args.sequence_filename, "r") as sequence_fd:
            sequence = ExperimentSequence(args.sequence_filename, sequence_fd.read())

        runner = ExperimentRunner(self.config, sequence)
        runner.start()

        with Sub0(dial=runner.subscription_address) as sub:
            sub.subscribe(b"")
            for index, experiment in enumerate(sequence.experiments):
                with wasabi.msg.loading(f"Experiment {experiment.name}"):
                    while True:
                        msg = sub.recv()
                        sequence_status = ExperimentSequenceStatus.from_msgpack(msg)
                        if (
                            sequence_status.experiments[index].state
                            == ExperimentState.FINISHED
                        ):
                            break
                wasabi.msg.good(f"Experiment {experiment.name}")
            runner.join()

        return 0
