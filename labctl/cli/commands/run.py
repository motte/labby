import sys
from wasabi import msg

from labctl.cli.core import auto_discover_experiments, BaseArgumentParser, Command
from labctl.experiment.runner import ExperimentRunner
from labctl.experiment.sequence import ExperimentSequence


# pyre-ignore[13]: command is unitialized
class RunArgumentParser(BaseArgumentParser):
    sequence_filename: str

    def add_arguments(self) -> None:
        self.add_argument("sequence_filename")


class RunCommand(Command[RunArgumentParser]):
    TRIGGER: str = "run"

    def main(self, args: RunArgumentParser) -> None:
        auto_discover_experiments()

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
