import sys


PY_36 = sys.version_info.major == 3 and sys.version_info.minor == 6
PY_37 = sys.version_info.major == 3 and sys.version_info.minor == 7
PY_38 = sys.version_info.major == 3 and sys.version_info.minor == 8


__all__ = ['PY_36', 'PY_37', 'PY_38']
