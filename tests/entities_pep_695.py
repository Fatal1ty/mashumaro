"""PEP 695 type alias entities for testing (cross-module imports)."""

from dataclasses import dataclass
from typing import Generic, List

from typing_extensions import TypeVar

from mashumaro import DataClassDictMixin
from mashumaro.types import GenericSerializableType

T = TypeVar("T")
from mashumaro.types import SerializableType, SerializationStrategy

# --- Simple type alias ---

type MyTypeAlias = int | str

# --- Generic type alias ---

type GenericAlias[T] = T | None

# --- Recursive type alias ---

type RecursiveIntList = int | list[RecursiveIntList]

# --- GenericSerializableType for use with type alias type args ---


class GenericListSerializable(Generic[T], GenericSerializableType):
    def __init__(self, value: List[T]):
        self.value = value

    def _serialize(self, types) -> List:
        return list(self.value)

    @classmethod
    def _deserialize(cls, value: List, types) -> "GenericListSerializable":
        return cls(value)

    def __eq__(self, other):
        return (
            isinstance(other, GenericListSerializable)
            and self.value == other.value
        )


class GenericPassthroughSerializable(Generic[T], GenericSerializableType):
    def __init__(self, value: T):
        self.value = value

    def _serialize(self, types) -> object:
        return self.value

    @classmethod
    def _deserialize(cls, value, types) -> "GenericPassthroughSerializable":
        return cls(value)

    def __eq__(self, other):
        return (
            isinstance(other, GenericPassthroughSerializable)
            and self.value == other.value
        )


# --- Boxed wrapper for recursive generic alias ---


class Boxed(Generic[T], GenericSerializableType):
    """Opaque wrapper that serializes its value as-is.

    Used as the recursive step in Nested[T] to avoid infinite codegen.
    """

    def __init__(self, value: T):
        self.value = value

    def _serialize(self, types) -> object:
        return self.value

    @classmethod
    def _deserialize(cls, value, types) -> "Boxed":
        return cls(value)

    def __eq__(self, other):
        return isinstance(other, Boxed) and self.value == other.value


# Recursive generic alias: the self-reference goes through Boxed (a
# GenericSerializableType) with a transformed type parameter, so codegen
# terminates but the alias is genuinely recursive.
type Nested[T] = T | Boxed[Nested[tuple[str, T]]]


# --- Dataclasses using these types ---


@dataclass
class DataClassWithParameterizedAlias(DataClassDictMixin):
    items: GenericListSerializable[GenericAlias[int]]


@dataclass
class DataClassWithWrappedRecursiveAlias(DataClassDictMixin):
    items: GenericPassthroughSerializable[RecursiveIntList]


@dataclass
class DataClassWithDirectRecursiveAlias(DataClassDictMixin):
    items: RecursiveIntList


@dataclass
class DataClassWithRecursiveGenericAlias(DataClassDictMixin):
    x: Nested[int]


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
