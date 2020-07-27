import fcntl
import re
import time
from enum import Enum
from dataclasses import dataclass
from types import TracebackType
from typing import Optional, Type

from serial import Serial


WAIT_TIME_AFTER_WRITE_MS: float = 50
TIMEOUT_MS = 2000


class PSUMode(Enum):
    CONSTANT_VOLTAGE = 0
    CONSTANT_CURRENT = 1


@dataclass(frozen=True)
class OperationalStatusRegister:
    mode: PSUMode


class TDKLambdaPSU:
    address: int
    baudrate: int
    port: str
    serial: Serial

    def __init__(
        self,
        port: str,
        baudrate: int,
        address: int = 1,
    ) -> None:
        self.address = address
        self.port = port
        self.baudrate = baudrate
        self.serial = Serial()

    def _write(self, msg: bytes) -> None:
        self.serial.write(msg)
        time.sleep(WAIT_TIME_AFTER_WRITE_MS / 1000.0)

    def __enter__(self) -> "TDKLambdaPSU":
        self.open()
        self._write(bytes(f":ADR{self.address:02d};", "utf-8"))
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> bool:
        self.close()
        return False

    def _read_line(self) -> str:
        return self.serial.readline()[:-2].decode("utf-8")

    def _read_operational_status_register(self) -> OperationalStatusRegister:
        self._write(b":STA?;")
        line = self._read_line()
        return OperationalStatusRegister(
            mode=PSUMode(int(line[2]))
        )

    def get_mode(self) -> PSUMode:
        return self._read_operational_status_register().mode

    def open(self) -> None:
        self.serial.port = self.port
        self.serial.baudrate = self.baudrate
        self.serial.xonxoff = True
        self.serial.timeout = TIMEOUT_MS / 1000.0
        self.serial.open()
        fcntl.flock(self.serial, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def close(self) -> None:
        self.serial.close()

    def get_model(self) -> str:
        self._write(b":MDL?;")
        return self._read_line()

    def is_output_on(self) -> bool:
        self._write(b":OUT?;")
        return self._read_line() == "OT1"

    def set_output_on(self, is_on: bool) -> None:
        self._write(b":OUT1;" if is_on else b":OUT0;")

    def get_software_version(self) -> str:
        self._write(b":REV?;")
        return self._read_line()

    def get_set_voltage(self) -> float:
        self._write(b":VOL!;")
        line = self._read_line()
        search = re.search("^SV([0-9]+\\.[0-9]+)$", line)
        return float(search.group(1))

    def get_actual_voltage(self) -> float:
        self._write(b":VOL?;")
        line = self._read_line()
        search = re.search("^AV([0-9]+\\.[0-9]+)$", line)
        return float(search.group(1))

    def get_set_current(self) -> float:
        self._write(b":CUR!;")
        line = self._read_line()
        search = re.search("^SA([0-9]+\\.[0-9]+)$", line)
        return float(search.group(1))

    def get_actual_current(self) -> float:
        self._write(b":CUR?;")
        line = self._read_line()
        search = re.search("^AA([0-9]+\\.[0-9]+)$", line)
        return float(search.group(1))

    def set_voltage(self, voltage: float) -> None:
        # TODO: assert voltage is within range
        command = bytes(f":VOL{voltage:.3f};", "utf-8")
        self._write(command)

    def set_current(self, current: float) -> None:
        # TODO: assert current is within range
        command = bytes(f":CUR{current:06.2f};", "utf-8")
        self._write(command)
