import io
import sys
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from typing import Iterator, Tuple


@contextmanager
def captured_output() -> Iterator[Tuple[io.StringIO, io.StringIO]]:
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        yield stdout, stderr
