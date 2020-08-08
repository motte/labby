import time
from unittest import TestCase

from labctl.tests.utils import patch_time


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
