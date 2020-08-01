import io
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from typing import Iterator, List, Tuple
from unittest.mock import patch, mock_open, Mock


@contextmanager
def captured_output() -> Iterator[Tuple[io.StringIO, io.StringIO]]:
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        yield stdout, stderr


@contextmanager
def cli_arguments(arguments: List[str]) -> Iterator[None]:
    with patch("sys.argv", ["labctl"] + arguments):
        yield


@contextmanager
def labctl_config(config_contents: str) -> Iterator[None]:
    with patch("builtins.open", mock_open(read_data=config_contents)):
        yield


def fake_serial_port(func) -> Iterator[Mock]:
    serial_port_mock = Mock()

    def wrapper(*args, **kwargs):
        with patch("time.sleep"), patch("labctl.hw.tdklambda.psu.fcntl.flock"), patch(
            "labctl.hw.core.Serial", return_value=serial_port_mock
        ):
            ret = func(*args, serial_port_mock, **kwargs)
        return ret

    return wrapper
