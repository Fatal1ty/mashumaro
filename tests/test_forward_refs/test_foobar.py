from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from mashumaro.mixins.json import DataClassJSONMixin

T = TypeVar("T")


@dataclass
class Foo(Generic[T], DataClassJSONMixin):
    x: T


@dataclass
class Bar(Foo[int]):
    pass
