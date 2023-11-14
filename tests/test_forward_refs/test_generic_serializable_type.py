from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Generic, TypeVar

from mashumaro import DataClassDictMixin
from mashumaro.types import SerializableType

T = TypeVar("T")


class Foo(Generic[T], SerializableType, use_annotations=True):
    a: T

    def __init__(self, a: T) -> None:
        self.a = a

    @classmethod
    def _deserialize(cls, value: Dict[str, T]) -> Foo[T]:
        return cls(**value)

    def _serialize(self) -> Dict[str, T]:
        return {"a": self.a}

    def __eq__(self, other: Foo) -> bool:
        return self.a == other.a


@dataclass
class Bar(DataClassDictMixin):
    x_str: Foo[str]
    x_date: Foo[date]


def test_generic_serializable_type():
    data = {"x_str": {"a": "2023-11-14"}, "x_date": {"a": "2023-11-14"}}
    obj = Bar(Foo("2023-11-14"), Foo(date(2023, 11, 14)))
    assert obj.to_dict() == data
    assert Bar.from_dict(data) == obj
