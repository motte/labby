import fcntl
import time
from abc import ABC, abstractmethod

from serial import Serial


class SerialDevice(ABC):
    WAIT_TIME_AFTER_WRITE_MS: float = 0.0

    serial: Serial

    def __init__(self, port: str, baudrate: int) -> None:
        self.serial = Serial()
        self.serial.port = port
        self.serial.baudrate = baudrate

    def _read_line(self) -> str:
        return self.serial.readline()[:-2].decode("utf-8")

    def _write(self, msg: bytes) -> None:
        self.serial.write(msg)
        time.sleep(self.WAIT_TIME_AFTER_WRITE_MS / 1000.0)

    def _query(self, msg: bytes) -> str:
        self._write(msg)
        return self._read_line()

    def open(self) -> None:
        self.serial.open()
        fcntl.flock(self.serial, fcntl.LOCK_EX | fcntl.LOCK_NB)
        self._on_open()

    def close(self) -> None:
        self.serial.close()

    @abstractmethod
    def _on_open(self) -> None:
        pass
