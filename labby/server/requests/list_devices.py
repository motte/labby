from dataclasses import dataclass
from typing import Optional, Sequence

from labby.hw.core import Device
from labby.server import Server, ServerRequest, ServerResponse, ServerResponseComponent


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
