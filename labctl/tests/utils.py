import io
import sys
from contextlib import contextmanager, redirect_stderr, redirect_stdout


@contextmanager
def captured_output():
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        yield stdout, stderr
