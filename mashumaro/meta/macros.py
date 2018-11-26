import sys


PY_36 = sys.version_info < (3, 7)
PY_37 = sys.version_info >= (3, 7)


__all__ = ['PY_36', 'PY_37']
