"""PEP 695 type alias entities for testing."""

from dataclasses import dataclass

from mashumaro import DataClassDictMixin
from mashumaro.types import SerializableType, SerializationStrategy


@dataclass(frozen=True, order=True)
class Leaf(DataClassDictMixin):
    v: int


# PEP 695 style generic serialization strategy
class PEP695GenericSetSortedSerializationStrategy[T2](SerializationStrategy):
    def serialize(self, value: set[T2]) -> list[T2]:
        return sorted(value)

    def deserialize(self, value: list[T2]) -> set[T2]:
        return set(value)


@dataclass
class DataClassWithPEP695SerializationStrategy(DataClassDictMixin):
    x: set[Leaf]

    class Config:
        serialization_strategy = {
            set: PEP695GenericSetSortedSerializationStrategy()
        }


# PEP 695 style generic serializable type with use_annotations=True
class PEP695GenericSerializableList[T](SerializableType, use_annotations=True):
    def __init__(self, value: list[T]):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.value == other.value

    def _serialize(self) -> list[T]:
        return self.value

    @classmethod
    def _deserialize(
        cls, value: list[T]
    ) -> "PEP695GenericSerializableList[T]":
        return cls(value)


@dataclass
class DataClassWithPEP695SerializableType(DataClassDictMixin):
    x: PEP695GenericSerializableList[str]
