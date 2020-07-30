import io
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from typing import Iterator, List, Tuple
from unittest.mock import patch


@contextmanager
def captured_output() -> Iterator[Tuple[io.StringIO, io.StringIO]]:
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        yield stdout, stderr


@contextmanager
def cli_arguments(arguments: List[str]) -> Iterator[None]:
    with patch("sys.argv", ["labctl"] + arguments):
        yield
