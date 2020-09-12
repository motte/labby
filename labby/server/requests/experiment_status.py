from dataclasses import dataclass
from typing import Optional

from labby.server import ExperimentSequenceStatus, Server, ServerResponse, ServerRequest


@dataclass(frozen=True)
class ExperimentStatusResponse(ServerResponse):
    sequence_status: Optional[ExperimentSequenceStatus]


@dataclass(frozen=True)
class ExperimentStatusRequest(ServerRequest[ExperimentStatusResponse]):
    def handle(self, server: Server) -> ExperimentStatusResponse:
        return ExperimentStatusResponse(
            sequence_status=server.get_experiment_sequence_status()
        )
