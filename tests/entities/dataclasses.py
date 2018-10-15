import collections
from dataclasses import dataclass
from typing import List, Deque, Tuple, Set, FrozenSet, ChainMap, Dict

from mashumaro import DataClassDictMixin
from tests.entities.abstract import (
    AbstractSet,
    AbstractMutableSet,
    AbstractMapping,
    AbstractMutableMapping,
    AbstractByteString,
    AbstractSequence,
    AbstractMutableSequence,
)
from tests.entities.custom import (
    CustomSerializableList,
    CustomSerializableDeque,
    CustomSerializableTuple,
    CustomSerializableSet,
    CustomSerializableFrozenSet,
    CustomSerializableChainMap,
    CustomSerializableMapping,
    CustomSerializableBytes,
    CustomSerializableByteArray,
    CustomSerializableSequence,
    CustomSerializableMutableSequence,
)
from tests.entities.enums import (
    MyEnum,
    MyIntEnum,
    MyFlag,
    MyIntFlag,
)


# simple types
@dataclass
class DataClassWithInt(DataClassDictMixin):
    x: int


# list
@dataclass
class DataClassWithList(DataClassDictMixin):
    x: list


@dataclass
class DataClassWithGenericList(DataClassDictMixin):
    x: List[int]


@dataclass
class DataClassWithCustomSerializableList(DataClassDictMixin):
    x: CustomSerializableList


# deque
@dataclass
class DataClassWithDeque(DataClassDictMixin):
    x: collections.deque


@dataclass
class DataClassWithGenericDeque(DataClassDictMixin):
    x: Deque[int]


@dataclass
class DataClassWithCustomSerializableDeque(DataClassDictMixin):
    x: CustomSerializableDeque


# tuple
@dataclass
class DataClassWithTuple(DataClassDictMixin):
    x: tuple


@dataclass
class DataClassWithGenericTuple(DataClassDictMixin):
    x: Tuple[int]


@dataclass
class DataClassWithCustomSerializableTuple(DataClassDictMixin):
    x: CustomSerializableTuple


# set
@dataclass
class DataClassWithSet(DataClassDictMixin):
    x: set


@dataclass
class DataClassWithGenericSet(DataClassDictMixin):
    x: Set[int]


@dataclass
class DataClassWithCustomSerializableSet(DataClassDictMixin):
    x: CustomSerializableSet


@dataclass
class DataClassWithAbstractSet(DataClassDictMixin):
    x: AbstractSet


@dataclass
class DataClassWithAbstractMutableSet(DataClassDictMixin):
    x: AbstractMutableSet


# frozenset
@dataclass
class DataClassWithFrozenSet(DataClassDictMixin):
    x: frozenset


@dataclass
class DataClassWithGenericFrozenSet(DataClassDictMixin):
    x: FrozenSet[int]


@dataclass
class DataClassWithCustomSerializableFrozenSet(DataClassDictMixin):
    x: CustomSerializableFrozenSet


# ChainMap
@dataclass
class DataClassWithChainMap(DataClassDictMixin):
    x: collections.ChainMap


@dataclass
class DataClassWithGenericChainMap(DataClassDictMixin):
    x: ChainMap[int, int]


@dataclass
class DataClassWithCustomSerializableChainMap(DataClassDictMixin):
    x: CustomSerializableChainMap


# dict
@dataclass
class DataClassWithDict(DataClassDictMixin):
    x: dict


@dataclass
class DataClassWithGenericDict(DataClassDictMixin):
    x: Dict[int, int]


@dataclass
class DataClassWithCustomSerializableMapping(DataClassDictMixin):
    x: CustomSerializableMapping


@dataclass
class DataClassWithAbstractMapping(DataClassDictMixin):
    x: AbstractMapping


@dataclass
class DataClassWithAbstractMutableMapping(DataClassDictMixin):
    x: AbstractMutableMapping


# bytes, bytearray
@dataclass
class DataClassWithBytes(DataClassDictMixin):
    x: bytes


@dataclass
class DataClassWithByteArray(DataClassDictMixin):
    x: bytearray


@dataclass
class DataClassWithCustomSerializableBytes(DataClassDictMixin):
    x: CustomSerializableBytes


@dataclass
class DataClassWithCustomSerializableByteArray(DataClassDictMixin):
    x: CustomSerializableByteArray


@dataclass
class DataClassWithAbstractByteString(DataClassDictMixin):
    x: AbstractByteString


# str
@dataclass
class DataClassWithStr(DataClassDictMixin):
    x: str


# sequence
@dataclass
class DataClassWithCustomSerializableSequence(DataClassDictMixin):
    x: CustomSerializableSequence


@dataclass
class DataClassWithCustomSerializableMutableSequence(DataClassDictMixin):
    x: CustomSerializableMutableSequence


@dataclass
class DataClassWithAbstractSequence(DataClassDictMixin):
    x: AbstractSequence


@dataclass
class DataClassWithAbstractMutableSequence(DataClassDictMixin):
    x: AbstractMutableSequence


@dataclass
class DataClassWithEnum(DataClassDictMixin):
    x: MyEnum


@dataclass
class DataClassWithIntEnum(DataClassDictMixin):
    x: MyIntEnum


@dataclass
class DataClassWithFlag(DataClassDictMixin):
    x: MyFlag


@dataclass
class DataClassWithIntFlag(DataClassDictMixin):
    x: MyIntFlag
