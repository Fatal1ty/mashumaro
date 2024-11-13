from collections.abc import Generator
from contextlib import contextmanager
from typing import Optional

__all__ = ["CodeLines"]


class CodeLines:
    def __init__(self) -> None:
        self._lines: list[str] = []
        self._current_indent: str = ""

    def append(self, line: str) -> None:
        self._lines.append(f"{self._current_indent}{line}")

    def extend(self, lines: "CodeLines") -> None:
        for line in lines._lines:
            self._lines.append(f"{self._current_indent}{line}")

    @contextmanager
    def indent(
        self,
        expr: Optional[str] = None,
    ) -> Generator[None, None, None]:
        if expr:
            self.append(expr)
        self._current_indent += " " * 4
        try:
            yield
        finally:
            self._current_indent = self._current_indent[:-4]

    def as_text(self) -> str:
        return "\n".join(self._lines)

    def reset(self) -> None:
        self._lines = []
        self._current_indent = ""
