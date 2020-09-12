import sys


if sys.version_info >= (3, 8):
    from typing import get_args
else:
    from typing import Any, Tuple

    def get_args(tp: Any) -> Tuple[Any, ...]:
        return tp.__args__
