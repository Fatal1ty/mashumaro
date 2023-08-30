from __future__ import annotations

from typing_extensions import TypedDict

from .bar import Bar


class Foo(TypedDict):
    bar: Bar
