from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Generic, TypeVar

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig
from mashumaro.types import SerializationStrategy

T = TypeVar("T")


class Foo(Generic[T]):
    a: T

    def __init__(self, a: T) -> None:
        self.a = a

    def __eq__(self, other: Foo) -> bool:
        return self.a == other.a


class FooStrategy(Generic[T], SerializationStrategy):
    def deserialize(self, value: Dict[str, T]) -> Foo[T]:
        return Foo(**value)

    def serialize(self, value: Foo[T]) -> Dict[str, T]:
        return {"a": value.a}


@dataclass
class Bar(DataClassDictMixin):
    x_str: Foo[str]
    x_date: Foo[date]

    class Config(BaseConfig):
        serialization_strategy = {Foo: FooStrategy()}


def test_generic_serialization_strategy():
    data = {"x_str": {"a": "2023-11-14"}, "x_date": {"a": "2023-11-14"}}
    obj = Bar(Foo("2023-11-14"), Foo(date(2023, 11, 14)))
    assert obj.to_dict() == data
    assert Bar.from_dict(data) == obj
