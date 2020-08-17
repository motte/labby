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
    Sequence,
    Type,
    TypeVar,
    Union,
    cast,
    get_args,
)

from mashumaro import DataClassMessagePackMixin
from mashumaro.serializer.msgpack import EncodedData
from pynng import Rep0, Req0, Sub0

from labby.config import Config
from labby.experiment.runner import ExperimentRunner, ExperimentSequenceStatus
from labby.experiment.sequence import ExperimentSequence
from labby.hw.core import Device, DeviceType
from labby.hw.core.power_supply import PowerSupply, PowerSupplyMode
from labby.utils import auto_discover_experiments, auto_discover_drivers


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


@dataclass(frozen=True)
class HaltRequest(ServerRequest[None]):
    def handle(self, server: "Server") -> None:
        sys.exit(0)


@dataclass(frozen=True)
class HelloWorldResponse(ServerResponse):
    content: str


@dataclass(frozen=True)
class HelloWorldRequest(ServerRequest[HelloWorldResponse]):
    def handle(self, server: "Server") -> HelloWorldResponse:
        return HelloWorldResponse(content="Hello world")


@dataclass(frozen=True)
class DeviceStatus(ServerResponseComponent):
    name: str
    is_available: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None


@dataclass(frozen=True)
class ListDevicesResponse(ServerResponse):
    devices: Sequence[DeviceStatus]


@dataclass(frozen=True)
class ListDevicesRequest(ServerRequest[ListDevicesResponse]):
    def _get_device_status(self, device: Device) -> DeviceStatus:
        try:
            device.open()
            device.test_connection()
            return DeviceStatus(name=str(device.name), is_available=True)
        except Exception as ex:
            return DeviceStatus(
                name=str(device.name),
                is_available=False,
                error_type=type(ex).__name__,
                error_message=str(ex),
            )
        finally:
            device.close()

    def handle(self, server: "Server") -> ListDevicesResponse:
        return ListDevicesResponse(
            devices=[
                self._get_device_status(device) for device in server.config.devices
            ]
        )


@dataclass(frozen=True)
class PowerSupplyInfo(ServerResponseComponent):
    is_output_on: bool
    mode: PowerSupplyMode
    target_voltage: float
    target_current: float
    actual_voltage: float
    actual_current: float


@dataclass(frozen=True)
class DeviceInfoResponse(ServerResponse):
    device_type: Optional[DeviceType]
    is_connected: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    power_supply_info: Optional[PowerSupplyInfo] = None


@dataclass(frozen=True)
class DeviceInfoRequest(ServerRequest[DeviceInfoResponse]):
    device_name: str

    def _get_power_supply_info(self, power_supply: PowerSupply) -> PowerSupplyInfo:
        return PowerSupplyInfo(
            is_output_on=power_supply.is_output_on(),
            mode=power_supply.get_mode(),
            target_voltage=power_supply.get_target_voltage(),
            target_current=power_supply.get_target_current(),
            actual_voltage=power_supply.get_actual_voltage(),
            actual_current=power_supply.get_actual_current(),
        )

    def _get_device_info(self, device: Device) -> ServerResponseComponent:
        device.open()
        device.test_connection()

        if device.device_type == DeviceType.POWER_SUPPLY:
            assert isinstance(device, PowerSupply)
            return self._get_power_supply_info(device)
        raise NotImplementedError

    def _get_key_name(self, device_type: DeviceType) -> str:
        if device_type == DeviceType.POWER_SUPPLY:
            return "power_supply_info"
        raise NotImplementedError

    def handle(self, server: "Server") -> DeviceInfoResponse:
        config = server.config

        try:
            device = next(
                device for device in config.devices if device.name == self.device_name
            )
        except StopIteration:
            return DeviceInfoResponse(device_type=None, is_connected=False)

        try:
            device_info = self._get_device_info(device)
            is_connected = True
            error_type = None
            error_message = None
        except Exception as ex:
            device_info = None
            error_type = type(ex).__name__
            error_message = str(ex)
            is_connected = False

        return DeviceInfoResponse(
            device_type=device.device_type,
            is_connected=is_connected,
            error_type=error_type,
            error_message=error_message,
            # pyre-ignore[6]: ugh super hacky
            **{self._get_key_name(device.device_type): device_info},
        )


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
        child_pid = os.fork()
        address = _ADDRESS
        if child_pid != 0:
            return ServerInfo(address=address, existing=False, pid=child_pid)

        with Rep0(listen=address) as rep:
            self._run(rep)

        # pyre-ignore[7]: this never returns anything on the child process
        sys.exit(0)

    def set_experiment_sequence_status(
        self, experiment_sequence_status: ExperimentSequenceStatus,
    ) -> None:
        with self._experiment_sequence_status_lock:
            self._experiment_sequence_status = copy.deepcopy(experiment_sequence_status)

    def get_experiment_sequence_status(self) -> Optional[ExperimentSequenceStatus]:
        with self._experiment_sequence_status_lock:
            return copy.deepcopy(self._experiment_sequence_status)

    def _run(self, socket: Rep0) -> None:
        while True:
            message = socket.recv()
            response = ServerRequest.handle_from_msgpack(self, message)
            if response is not None:
                socket.send(response)


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
            pass
        runner.start()


@dataclass(frozen=True)
class ExperimentStatusResponse(ServerResponse):
    sequence_status: Optional[ExperimentSequenceStatus]


@dataclass(frozen=True)
class ExperimentStatusRequest(ServerRequest[ExperimentStatusResponse]):
    def handle(self, server: "Server") -> ExperimentStatusResponse:
        return ExperimentStatusResponse(
            sequence_status=server.get_experiment_sequence_status()
        )


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

    def list_devices(self) -> ListDevicesResponse:
        return self._query(ListDevicesRequest())

    def device_info(self, device_name: str) -> DeviceInfoResponse:
        return self._query(DeviceInfoRequest(device_name=device_name))

    def run_sequence(self, sequence_filename: str) -> None:
        self._send(RunSequenceRequest(sequence_filename))

    def experiment_status(self) -> ExperimentStatusResponse:
        return self._query(ExperimentStatusRequest())

    def close(self) -> None:
        self.req.close()
