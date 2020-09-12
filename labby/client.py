from typing import cast

from pynng import Req0

from labby.server import (
    DeviceInfoRequest,
    DeviceInfoResponse,
    ExperimentStatusRequest,
    ExperimentStatusResponse,
    HaltRequest,
    HelloWorldRequest,
    ListDevicesRequest,
    ListDevicesResponse,
    RunSequenceRequest,
    ServerRequest,
    TNonOptionalResponse,
)


DEFAULT_CLIENT_TIMEOUT = 1000


class Client:
    req: Req0

    def __init__(self, address: str) -> None:
        self.req = Req0(
            dial=address,
            recv_timeout=DEFAULT_CLIENT_TIMEOUT,
            send_timeout=DEFAULT_CLIENT_TIMEOUT,
        )

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
