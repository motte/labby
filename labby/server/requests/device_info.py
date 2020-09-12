from dataclasses import dataclass
from typing import Optional

from labby.hw.core import Device, DeviceType
from labby.hw.core.power_supply import PowerSupply, PowerSupplyMode
from labby.server import Server, ServerRequest, ServerResponse, ServerResponseComponent


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
        device.test_connection()

        if device.device_type == DeviceType.POWER_SUPPLY:
            assert isinstance(device, PowerSupply)
            return self._get_power_supply_info(device)
        raise NotImplementedError

    def _get_key_name(self, device_type: DeviceType) -> str:
        if device_type == DeviceType.POWER_SUPPLY:
            return "power_supply_info"
        raise NotImplementedError

    def handle(self, server: Server) -> DeviceInfoResponse:
        config = server.config

        try:
            device = next(
                device for device in config.devices if device.name == self.device_name
            )
        except StopIteration:
            return DeviceInfoResponse(device_type=None, is_connected=False)

        try:
            device.open()
            device_info = self._get_device_info(device)
            is_connected = True
            error_type = None
            error_message = None
        except Exception as ex:
            device_info = None
            error_type = type(ex).__name__
            error_message = str(ex)
            is_connected = False
        finally:
            device.close()

        return DeviceInfoResponse(
            device_type=device.device_type,
            is_connected=is_connected,
            error_type=error_type,
            error_message=error_message,
            # pyre-ignore[6]: ugh super hacky
            **{self._get_key_name(device.device_type): device_info},
        )
