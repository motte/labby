import io
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from typing import Iterator, List, Tuple
from unittest.mock import patch, mock_open


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
