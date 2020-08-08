import time
from typing import Generator
from unittest import TestCase

from labby.tests.utils import patch_time


class UtilsTest(TestCase):
    def _current_time(self) -> str:
        now = time.time()
        return time.asctime(time.gmtime(now))

    def test_patch_time(self) -> None:
        with patch_time("2020-08-08"):
            self.assertEquals(self._current_time(), "Sat Aug  8 00:00:00 2020")
            time.sleep(1)
            self.assertEquals(self._current_time(), "Sat Aug  8 00:00:01 2020")
            time.sleep(3600)
            self.assertEquals(self._current_time(), "Sat Aug  8 01:00:01 2020")

    def test_patch_time_with_ticker(self) -> None:
        state: str = "unitialized"

        def _ticker() -> Generator[float, None, None]:
            nonlocal state
            state = "initial_state"
            yield 0.0
            state = "]0s, 1s]"
            yield 1.0
            state = "]1s, 1.5s]"
            yield 1.5
            state = "]1.5s, 2s]"
            yield 2
            state = "end_state"

        with patch_time("2020-08-08", _ticker()):
            self.assertEquals(state, "initial_state")
            time.sleep(0.01)
            self.assertEquals(state, "]0s, 1s]")
            time.sleep(0.98)
            self.assertEquals(state, "]0s, 1s]")
            self.assertEquals(self._current_time(), "Sat Aug  8 00:00:00 2020")
            time.sleep(0.01)
            self.assertEquals(self._current_time(), "Sat Aug  8 00:00:01 2020")
            self.assertEquals(state, "]0s, 1s]")

            # state change (t=1.01)
            time.sleep(0.01)
            self.assertEquals(state, "]1s, 1.5s]")
            time.sleep(0.49)
            self.assertEquals(state, "]1s, 1.5s]")

            # state change (t=1.51)
            time.sleep(0.01)
            self.assertEquals(state, "]1.5s, 2s]")
            self.assertEquals(self._current_time(), "Sat Aug  8 00:00:01 2020")
            time.sleep(0.49)
            self.assertEquals(self._current_time(), "Sat Aug  8 00:00:02 2020")
            self.assertEquals(state, "]1.5s, 2s]")

            # state change (t=2.01)
            time.sleep(0.01)
            self.assertEquals(state, "end_state")

            # state change (t=2.01)
            time.sleep(3600.0)
            self.assertEquals(state, "end_state")
            self.assertEquals(self._current_time(), "Sat Aug  8 01:00:02 2020")
