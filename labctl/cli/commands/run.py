import sys
from importlib import import_module
from pathlib import Path
from wasabi import msg

from labctl.cli.core import BaseArgumentParser, Command
from labctl.experiment.runner import ExperimentRunner
from labctl.experiment.sequence import ExperimentSequence


# pyre-ignore[13]: command is unitialized
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

    def main(self, args: RunArgumentParser) -> None:
        self._auto_discover_experiments()

        filename = args.sequence_filename
        if filename is None:
            sys.exit(1)
        with open(filename, "r") as sequence_fd:
            sequence = ExperimentSequence(sequence_fd.read())

        runner = ExperimentRunner(self.config)
        for index, experiment in enumerate(sequence.experiments):
            with msg.loading(f"Experiment {index}"):
                runner.run_experiment(experiment)
            msg.good(f"Experiment {index}")
