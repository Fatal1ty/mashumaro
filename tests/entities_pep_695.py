"""PEP 695 type alias entities for testing (cross-module imports)."""

from dataclasses import dataclass
from typing import Generic, List

from typing_extensions import TypeVar

from mashumaro import DataClassDictMixin
from mashumaro.types import GenericSerializableType

T = TypeVar("T")

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
