import copy
import os
import sys
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import (
    Dict,
    Generic,
    Optional,
    Type,
    TypeVar,
    Union,
    cast,
)

from mashumaro import DataClassMessagePackMixin
from mashumaro.serializer.msgpack import EncodedData
from pynng import Rep0

from labby.config import Config
from labby.experiment.runner import ExperimentSequenceStatus
from labby.utils import auto_discover_drivers
from labby.utils.typing import get_args


_ADDRESS = "tcp://127.0.0.1:14337"


@dataclass(frozen=True)
class ServerInfo:
    address: str
    existing: bool
    pid: int


@dataclass(frozen=True)
class ServerResponseComponent(DataClassMessagePackMixin, ABC):
    pass


ServerResponse = ServerResponseComponent


TResponse = TypeVar("TResponse", bound=Union[None, ServerResponse])
TNonOptionalResponse = TypeVar("TResponse", bound=ServerResponse)
_ALL_REQUEST_TYPES: Dict[str, Type["ServerRequest[ServerResponse]"]] = {}


@dataclass(frozen=True)
class ServerRequest(Generic[TResponse], DataClassMessagePackMixin, ABC):
    def __init_subclass__(cls: Type["ServerRequest[ServerResponse]"]) -> None:
        _ALL_REQUEST_TYPES[cls.__name__] = cls
        super().__init_subclass__()

    def get_response_type(cls) -> TResponse:
        # pyre-ignore[16]: pyre does not understand __orig_bases__
        return get_args(cls.__orig_bases__[0])[0]

    @classmethod
    def handle_from_msgpack(
        cls, server: "Server", msg: EncodedData
    ) -> Optional[EncodedData]:
        (request_type, msg) = cast(bytes, msg).split(b":", 1)
        klass = _ALL_REQUEST_TYPES[request_type.decode()]
        request = klass.from_msgpack(msg)
        response = request.handle(server)
        if response is None:
            return None
        return response.to_msgpack()

    @abstractmethod
    def handle(self, server: "Server") -> TResponse:
        raise NotImplementedError


class Server:
    config: Config
    _experiment_sequence_status_lock: threading.Lock
    _experiment_sequence_status: Optional[ExperimentSequenceStatus]

    def __init__(self, config_filename: str = "labby.yml") -> None:
        self.config_filename = config_filename
        self._experiment_sequence_status = None
        self._experiment_sequence_status_lock = threading.Lock()

        auto_discover_drivers()
        with open(self.config_filename, "r") as config_file:
            self.config = Config(config_file.read())

    def start(self) -> ServerInfo:
        address = _ADDRESS

        existing_pid = self.get_existing_pid()
        if existing_pid:
            return ServerInfo(address=address, existing=True, pid=existing_pid)

        child_pid = os.fork()
        if child_pid != 0:
            self._create_pid_file(child_pid)
            return ServerInfo(address=address, existing=False, pid=child_pid)

        with Rep0(listen=address) as rep:
            self._run(rep)

        # pyre-ignore[7]: this never returns anything on the child process
        sys.exit(0)

    def stop(self) -> None:
        sys.exit(0)

    @classmethod
    def get_existing_pid(cls) -> Optional[int]:
        try:
            with open(".labby/pid", "r") as pid_file:
                return int(pid_file.read())
        except (FileNotFoundError, ValueError):
            return None

    def _create_pid_file(cls, pid: int) -> Optional[int]:
        os.makedirs(".labby", exist_ok=True)
        with open(".labby/pid", "w") as pid_file:
            pid_file.write(str(pid))

    def _delete_pid_file(self) -> None:
        try:
            os.remove(".labby/pid")
        except OSError:
            pass

    def set_experiment_sequence_status(
        self,
        experiment_sequence_status: ExperimentSequenceStatus,
    ) -> None:
        with self._experiment_sequence_status_lock:
            self._experiment_sequence_status = copy.deepcopy(experiment_sequence_status)

    def get_experiment_sequence_status(self) -> Optional[ExperimentSequenceStatus]:
        with self._experiment_sequence_status_lock:
            return copy.deepcopy(self._experiment_sequence_status)

    def _run(self, socket: Rep0) -> None:
        try:
            while True:
                message = socket.recv()
                response = ServerRequest.handle_from_msgpack(self, message)
                if response is not None:
                    socket.send(response)
        finally:
            self._delete_pid_file()
