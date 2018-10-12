from enum import Enum, IntEnum, Flag, IntFlag
import typing
import collections
from dataclasses import dataclass

from mashumaro import DataClassDictMixin
from tests.entities.abstract import *
from tests.entities.custom import *


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
    x: typing.List[int]


@dataclass
class DataClassWithCustomSerializableList(DataClassDictMixin):
    x: CustomSerializableList


# deque
@dataclass
class DataClassWithDeque(DataClassDictMixin):
    x: collections.deque


@dataclass
class DataClassWithGenericDeque(DataClassDictMixin):
    x: typing.Deque[int]


@dataclass
class DataClassWithCustomSerializableDeque(DataClassDictMixin):
    x: CustomSerializableDeque


# tuple
@dataclass
class DataClassWithTuple(DataClassDictMixin):
    x: tuple


@dataclass
class DataClassWithGenericTuple(DataClassDictMixin):
    x: typing.Tuple[int]


@dataclass
class DataClassWithCustomSerializableTuple(DataClassDictMixin):
    x: CustomSerializableTuple


# set
@dataclass
class DataClassWithSet(DataClassDictMixin):
    x: set


@dataclass
class DataClassWithGenericSet(DataClassDictMixin):
    x: typing.Set[int]


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
    x: typing.FrozenSet[int]


@dataclass
class DataClassWithCustomSerializableFrozenSet(DataClassDictMixin):
    x: CustomSerializableFrozenSet


# ChainMap
@dataclass
class DataClassWithChainMap(DataClassDictMixin):
    x: collections.ChainMap


@dataclass
class DataClassWithGenericChainMap(DataClassDictMixin):
    x: typing.ChainMap[int, int]


@dataclass
class DataClassWithCustomSerializableChainMap(DataClassDictMixin):
    x: CustomSerializableChainMap


# dict
@dataclass
class DataClassWithDict(DataClassDictMixin):
    x: dict


@dataclass
class DataClassWithGenericDict(DataClassDictMixin):
    x: typing.Dict[int, int]


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


class MyEnum(Enum):
    a = 'a'
    b = 'b'


class MyIntEnum(IntEnum):
    a = 1
    b = 2


class MyFlag(Flag):
    a = 1
    b = 2


class MyIntFlag(IntFlag):
    a = 1
    b = 2


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
