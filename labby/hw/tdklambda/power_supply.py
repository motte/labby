import re
from dataclasses import dataclass
from typing import Match

from labby.hw.core.power_supply import (
    PowerSupply,
    PowerSupplyMode,
)
from labby.hw.core.exceptions import HardwareIOError
from labby.hw.core.serial import SerialDevice


@dataclass(frozen=True)
class OperationalStatusRegister:
    mode: PowerSupplyMode


class ZUP(SerialDevice, PowerSupply):
    WAIT_TIME_AFTER_WRITE_MS: float = 50.0

    address: int

    def __init__(self, port: str, baudrate: int, address: int = 1,) -> None:
        SerialDevice.__init__(self, port, baudrate)
        self.address = address

    def __enter__(self) -> "ZUP":
        PowerSupply.__enter__(self)
        return self

    def _on_open(self) -> None:
        self._write(bytes(f":ADR{self.address:02d};", "utf-8"))

    def _read_operational_status_register(self) -> OperationalStatusRegister:
        response = self._query(b":STA?;")
        return OperationalStatusRegister(mode=PowerSupplyMode(int(response[2])))

    def get_mode(self) -> PowerSupplyMode:
        return self._read_operational_status_register().mode

    def test_connection(self) -> None:
        try:
            model = self.get_model()
            assert len(model) > 0
        except Exception:
            raise HardwareIOError

    def get_model(self) -> str:
        return self._query(b":MDL?;")

    def is_output_on(self) -> bool:
        return self._query(b":OUT?;") == "OT1"

    def set_output_on(self, is_on: bool) -> None:
        self._write(b":OUT1;" if is_on else b":OUT0;")

    def get_software_version(self) -> str:
        return self._query(b":REV?;")

    def _re_search(self, regex: str, line: str) -> Match[str]:
        search = re.search(regex, line)
        if search is None:
            raise HardwareIOError(f"Could not parse response: {line}")
        return search

    def get_target_voltage(self) -> float:
        response = self._query(b":VOL!;")
        search = self._re_search("^SV([0-9]+\\.[0-9]+)$", response)
        return float(search.group(1))

    def get_actual_voltage(self) -> float:
        response = self._query(b":VOL?;")
        search = self._re_search("^AV([0-9]+\\.[0-9]+)$", response)
        return float(search.group(1))

    def get_target_current(self) -> float:
        response = self._query(b":CUR!;")
        search = self._re_search("^SA([0-9]+\\.[0-9]+)$", response)
        return float(search.group(1))

    def get_actual_current(self) -> float:
        response = self._query(b":CUR?;")
        search = self._re_search("^AA([0-9]+\\.[0-9]+)$", response)
        return float(search.group(1))

    def set_target_voltage(self, voltage: float) -> None:
        # TODO: assert voltage is within range
        command = bytes(f":VOL{voltage:.3f};", "utf-8")
        self._write(command)

    def set_target_current(self, current: float) -> None:
        # TODO: assert current is within range
        command = bytes(f":CUR{current:06.2f};", "utf-8")
        self._write(command)
