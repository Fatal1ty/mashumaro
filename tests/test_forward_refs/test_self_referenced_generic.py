from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Generic, Optional, TypeVar

from mashumaro.mixins.json import DataClassJSONMixin

T = TypeVar("T")


@dataclass
class Foo(Generic[T], DataClassJSONMixin):
    x: T
    y: Optional[Foo[Any]]


@dataclass
class Bar(Foo): ...


def test_self_referenced_generic_no_max_recursion_error():
    obj = Bar(42, Foo(33, None))
    assert obj.to_dict() == {"x": 42, "y": {"x": 33, "y": None}}
    assert Bar.from_dict({"x": 42, "y": {"x": 33, "y": None}}) == obj
    assert obj.to_json() == '{"x": 42, "y": {"x": 33, "y": null}}'
    assert Bar.from_json('{"x": 42, "y": {"x": 33, "y": null}}') == obj
