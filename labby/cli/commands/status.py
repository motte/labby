from wasabi import msg

from labby.cli.core import BaseArgumentParser, Command
from labby.experiment.runner import ExperimentState
from labby.server.requests.experiment_status import ExperimentStatusResponse


class StatusCommand(Command[BaseArgumentParser]):
    TRIGGER: str = "status"

    def main(self, args: BaseArgumentParser) -> int:
        response: ExperimentStatusResponse = self.client.experiment_status()
        sequence_status = response.sequence_status

        if sequence_status is None:
            print("There are no experiments running.")
            return 0

        for experiment in sequence_status.experiments:
            if experiment.state == ExperimentState.FINISHED:
                msg.good(experiment.name)
            elif experiment.state == ExperimentState.RUNNING:
                progress = round(experiment.progress * 100)
                msg.text(f"\u25b6 {experiment.name} ({progress}%)")
            elif experiment.state == ExperimentState.NOT_STARTED:
                msg.text(f"  {experiment.name}", color="grey")

        return 0
