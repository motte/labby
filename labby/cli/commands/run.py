import wasabi
from pynng import Sub0

from labby.cli.core import BaseArgumentParser, Command
from labby.experiment.runner import ExperimentRunner, ExperimentSequenceStatus
from labby.experiment.sequence import ExperimentSequence
from labby.utils import auto_discover_experiments


# pyre-ignore[13]: sequence_filename is unitialized
class RunArgumentParser(BaseArgumentParser):
    sequence_filename: str

    def add_arguments(self) -> None:
        self.add_argument("sequence_filename")


class RunCommand(Command[RunArgumentParser]):
    TRIGGER: str = "run"

    def main(self, args: RunArgumentParser) -> int:
        auto_discover_experiments()

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
                        if sequence_status.experiments[index].is_finished():
                            break
                wasabi.msg.good(f"Experiment {experiment.name}")
            runner.join()

        return 0
