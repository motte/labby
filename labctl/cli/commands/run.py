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

        with open(args.sequence_filename, "r") as sequence_fd:
            sequence = ExperimentSequence(sequence_fd.read())

        for experiment in sequence.experiments:
            runner = ExperimentRunner(self.config, experiment)
            with msg.loading(f"Experiment {experiment.name}"):
                runner.run_experiment()
            msg.good(f"Experiment {experiment.name}")
