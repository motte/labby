import threading
import time
from dataclasses import dataclass

from pynng import Sub0

from labby.experiment.runner import ExperimentRunner, ExperimentSequenceStatus
from labby.experiment.sequence import ExperimentSequence
from labby.server import Server, ServerRequest
from labby.utils import auto_discover_experiments


@dataclass(frozen=True)
class RunSequenceRequest(ServerRequest[None]):
    sequence_filename: str

    def handle(self, server: Server) -> None:
        auto_discover_experiments()

        with open(self.sequence_filename, "r") as sequence_fd:
            sequence = ExperimentSequence(self.sequence_filename, sequence_fd.read())

        runner = ExperimentRunner(server.config, sequence)
        monitor = ExperimentMonitor(server, sequence, runner.subscription_address)

        monitor.start()
        while not monitor.has_started:
            time.sleep(0)
        runner.start()


class ExperimentMonitor(threading.Thread):
    sequence: ExperimentSequence
    server: Server
    subscription_address: str
    has_started: bool

    def __init__(
        self, server: Server, sequence: ExperimentSequence, subscription_address: str
    ) -> None:
        super().__init__()
        self.sequence = sequence
        self.server = server
        self.subscription_address = subscription_address
        self.has_started = False

    def run(self) -> None:
        with Sub0(dial=self.subscription_address) as sub:
            sub.subscribe(b"")
            self.has_started = True
            for index, experiment in enumerate(self.sequence.experiments):
                while True:
                    msg = sub.recv()
                    sequence_status = ExperimentSequenceStatus.from_msgpack(msg)
                    self.server.set_experiment_sequence_status(sequence_status)
                    if sequence_status.experiments[index].is_finished():
                        break
