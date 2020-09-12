from dataclasses import dataclass

from labby.server import Server, ServerRequest, ServerResponse


@dataclass(frozen=True)
class HelloWorldResponse(ServerResponse):
    content: str


@dataclass(frozen=True)
class HelloWorldRequest(ServerRequest[HelloWorldResponse]):
    def handle(self, server: "Server") -> HelloWorldResponse:
        return HelloWorldResponse(content="Hello world")
