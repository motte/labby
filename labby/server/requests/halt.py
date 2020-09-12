from dataclasses import dataclass

from labby.server import Server, ServerRequest


@dataclass(frozen=True)
class HaltRequest(ServerRequest[None]):
    def handle(self, server: Server) -> None:
        server.stop()
