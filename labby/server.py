import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Set, Type

from mashumaro import DataClassMessagePackMixin
from mashumaro.serializer.msgpack import EncodedData
from pynng import Rep0, Req0


_ADDRESS = "tcp://127.0.0.1:14337"


@dataclass(frozen=True)
class ServerInfo:
    address: str
    existing: bool
    pid: int


_ALL_REQUEST_TYPES: Set[Type["ServerRequest"]] = set([])


@dataclass(frozen=True)
class ServerRequest(DataClassMessagePackMixin, ABC):
    def __init_subclass__(cls) -> None:
        _ALL_REQUEST_TYPES.add(cls)

    @classmethod
    def handle_from_msgpack(cls, msg: EncodedData) -> None:
        for klass in _ALL_REQUEST_TYPES:
            try:
                request = klass.from_msgpack(msg)
                klass.handle(request)
            except Exception:
                pass

    @abstractmethod
    def handle(self) -> None:
        raise NotImplementedError


@dataclass(frozen=True)
class HaltRequest(ServerRequest):
    def handle(self) -> None:
        sys.exit(0)


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
        while True:
            message = socket.recv()
            ServerRequest.handle_from_msgpack(message)


class Client:
    req: Req0

    def __init__(self, address: str) -> None:
        self.req = Req0(dial=address)

    def halt(self) -> None:
        self.req.send(HaltRequest().to_msgpack())

    def close(self) -> None:
        self.req.close()
