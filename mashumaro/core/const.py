import enum
import sys

__all__ = [
    "PY_37",
    "PY_38",
    "PY_39",
    "PY_310",
    "PY_37_MIN",
    "PY_38_MIN",
    "PY_39_MIN",
    "PY_310_MIN",
    "PY_311_MIN",
    "PEP_585_COMPATIBLE",
    "PEP_586_COMPATIBLE",
    "Sentinel",
]


PY_37 = sys.version_info.major == 3 and sys.version_info.minor == 7
PY_38 = sys.version_info.major == 3 and sys.version_info.minor == 8
PY_39 = sys.version_info.major == 3 and sys.version_info.minor == 9
PY_310 = sys.version_info.major == 3 and sys.version_info.minor == 10
PY_311 = sys.version_info.major == 3 and sys.version_info.minor == 11
PY_312_MIN = sys.version_info.major == 3 and sys.version_info.minor >= 12

PY_311_MIN = PY_311 or PY_312_MIN
PY_310_MIN = PY_310 or PY_311_MIN
PY_39_MIN = PY_39 or PY_310_MIN
PY_38_MIN = PY_38 or PY_39_MIN
PY_37_MIN = PY_37 or PY_38_MIN

PEP_585_COMPATIBLE = PY_39_MIN  # Type Hinting Generics In Standard Collections
PEP_586_COMPATIBLE = PY_38_MIN  # Literal Types


class Sentinel(enum.Enum):
    MISSING = enum.auto()
