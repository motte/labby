import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Generic, Optional, Type, TypeVar, Union, cast, get_args

from mashumaro import DataClassMessagePackMixin
from mashumaro.serializer.msgpack import EncodedData
from pynng import Rep0, Req0

from labby.config import Config
from labby.hw.core import auto_discover_drivers


_ADDRESS = "tcp://127.0.0.1:14337"


@dataclass(frozen=True)
class ServerInfo:
    address: str
    existing: bool
    pid: int


@dataclass(frozen=True)
class ServerResponse(DataClassMessagePackMixin, ABC):
    pass


TResponse = TypeVar("TResponse", bound=Union[None, ServerResponse])
TNonOptionalResponse = TypeVar("TResponse", bound=ServerResponse)
_ALL_REQUEST_TYPES: Dict[str, Type["ServerRequest[ServerResponse]"]] = {}


@dataclass(frozen=True)
class ServerRequest(Generic[TResponse], DataClassMessagePackMixin, ABC):
    def __init_subclass__(cls: Type["ServerRequest[ServerResponse]"]) -> None:
        _ALL_REQUEST_TYPES[cls.__name__] = cls

    def get_response_type(cls) -> TResponse:
        # pyre-ignore[16]: pyre does not understand __orig_bases__
        return get_args(cls.__orig_bases__[0])[0]

    @classmethod
    def handle_from_msgpack(
        cls, config: Config, msg: EncodedData
    ) -> Optional[EncodedData]:
        (request_type, msg) = cast(bytes, msg).split(b":", 1)
        klass = _ALL_REQUEST_TYPES[request_type.decode()]
        request = klass.from_msgpack(msg)
        response = request.handle(config)
        if response is None:
            return None
        return response.to_msgpack()

    @abstractmethod
    def handle(self, config: Config) -> TResponse:
        raise NotImplementedError


@dataclass(frozen=True)
class HaltRequest(ServerRequest[None]):
    def handle(self, config: Config) -> None:
        sys.exit(0)


@dataclass(frozen=True)
class HelloWorldResponse(ServerResponse):
    content: str


@dataclass(frozen=True)
class HelloWorldRequest(ServerRequest[HelloWorldResponse]):
    def handle(self, config: Config) -> HelloWorldResponse:
        return HelloWorldResponse(content="Hello world")


class Server:
    def start(self) -> ServerInfo:
        child_pid = os.fork()
        address = _ADDRESS
        if child_pid != 0:
            return ServerInfo(address=address, existing=False, pid=child_pid)

        with Rep0(listen=address) as rep:
            self._run(rep)

        # pyre-ignore[7]: this never returns anything on the child process
        sys.exit(0)

    def _run(self, socket: Rep0) -> None:
        auto_discover_drivers()
        # TODO read this from arguments
        with open("labby.yml", "r") as config_file:
            config = Config(config_file.read())

        while True:
            message = socket.recv()
            response = ServerRequest.handle_from_msgpack(config, message)
            if response is not None:
                socket.send(response)


class Client:
    req: Req0

    def __init__(self, address: str) -> None:
        self.req = Req0(dial=address)

    def _send(self, request: ServerRequest[None]) -> None:
        self.req.send(
            type(request).__name__.encode() + b":" + cast(bytes, request.to_msgpack())
        )

    def _query(
        self, request: ServerRequest[TNonOptionalResponse]
    ) -> TNonOptionalResponse:
        # FIXME: ughh I can't get rid of this copypasta
        self.req.send(
            type(request).__name__.encode() + b":" + cast(bytes, request.to_msgpack())
        )
        response_type = request.get_response_type()
        response = self.req.recv()
        return response_type.from_msgpack(response)

    def halt(self) -> None:
        self._send(HaltRequest())

    def hello(self) -> str:
        return self._query(HelloWorldRequest()).content

    def close(self) -> None:
        self.req.close()
