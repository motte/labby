import io
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from typing import Dict, Iterator, List, Tuple
from unittest.mock import patch, mock_open, MagicMock, Mock


@contextmanager
def captured_output() -> Iterator[Tuple[io.StringIO, io.StringIO]]:
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        yield stdout, stderr


@contextmanager
def cli_arguments(arguments: List[str]) -> Iterator[None]:
    with patch("sys.argv", ["labctl"] + arguments):
        yield


class _OpenMockFileStore:
    filename_to_mock: Dict[str, MagicMock] = {}

    def register(self, filename: str, contents: str) -> None:
        assert filename not in self.filename_to_mock.keys()
        mock = mock_open(read_data=contents)
        self.filename_to_mock[filename] = mock

    def unregister(self, filename: str) -> None:
        assert filename in self.filename_to_mock.keys()
        del self.filename_to_mock[filename]

    def open(self, filename: str, *args, **kwargs) -> MagicMock:
        return self.filename_to_mock[filename]()


OPEN_MOCK_FILE_STORE = _OpenMockFileStore()


@contextmanager
def patch_file_contents(filename: str, contents: str) -> Iterator[None]:
    OPEN_MOCK_FILE_STORE.register(filename, contents)
    try:
        with patch("builtins.open", OPEN_MOCK_FILE_STORE.open):
            yield
    finally:
        OPEN_MOCK_FILE_STORE.unregister(filename)


@contextmanager
def labctl_config(config_contents: str) -> Iterator[None]:
    with patch_file_contents("labctl.yml", config_contents):
        yield


def fake_serial_port(func) -> Iterator[Mock]:
    serial_port_mock = Mock()

    def wrapper(*args, **kwargs):
        with patch("time.sleep"), patch(
            "labctl.hw.tdklambda.power_supply.fcntl.flock"
        ), patch("labctl.hw.core.Serial", return_value=serial_port_mock):
            ret = func(*args, serial_port_mock, **kwargs)
        return ret

    return wrapper


ENV_VARIABLES: Dict[str, str] = {}


@contextmanager
def environment_variable(name: str, value: str) -> Iterator[None]:
    import os

    ENV_VARIABLES[name] = value
    with patch.dict(os.environ, ENV_VARIABLES):
        yield
    del ENV_VARIABLES[name]
