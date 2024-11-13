import enum
import sys

__all__ = [
    "PY_39",
    "PY_310",
    "PY_310_MIN",
    "PY_311_MIN",
    "PY_312_MIN",
    "PY_313_MIN",
    "Sentinel",
]


PY_39 = sys.version_info.major == 3 and sys.version_info.minor == 9
PY_310 = sys.version_info.major == 3 and sys.version_info.minor == 10
PY_311 = sys.version_info.major == 3 and sys.version_info.minor == 11
PY_312 = sys.version_info.major == 3 and sys.version_info.minor == 12
PY_313_MIN = sys.version_info.major == 3 and sys.version_info.minor >= 13

PY_312_MIN = PY_312 or PY_313_MIN
PY_311_MIN = PY_311 or PY_312_MIN
PY_310_MIN = PY_310 or PY_311_MIN


class Sentinel(enum.Enum):
    MISSING = enum.auto()
