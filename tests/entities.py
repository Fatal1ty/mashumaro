from dataclasses import dataclass
from enum import Enum, Flag, IntEnum, IntFlag
from os import PathLike
from typing import Any, Optional, TypeVar, Union

from mashumaro import DataClassDictMixin
from mashumaro.config import TO_DICT_ADD_OMIT_NONE_FLAG, BaseConfig
from mashumaro.types import SerializableType

T = TypeVar("T")
TAny = TypeVar("TAny", bound=Any)
TInt = TypeVar("TInt", bound=int)
TIntStr = TypeVar("TIntStr", int, str)
T_Optional_int = TypeVar("T_Optional_int", bound=Optional[int])


class MyEnum(Enum):
    a = "letter a"
    b = "letter b"


class MyStrEnum(str, Enum):
    a = "letter a"
    b = "letter b"


class MyIntEnum(IntEnum):
    a = 1
    b = 2


class MyFlag(Flag):
    a = 1
    b = 2


class MyIntFlag(IntFlag):
    a = 1
    b = 2


class MyList(list):
    pass


@dataclass
class MyDataClass(DataClassDictMixin):
    a: int
    b: int


class MutableString(SerializableType):
    def __init__(self, value: str):
        self.characters = [c for c in value]

    def _serialize(self) -> str:
        return str(self)

    @classmethod
    def _deserialize(cls, value: str) -> "MutableString":
        return MutableString(value)

    def __str__(self):
        return "".join(self.characters)

    def __eq__(self, other):
        return self.characters == other.characters


class CustomPath(PathLike):
    def __init__(self, *args: str):
        self._path = "/".join(args)

    def __fspath__(self):
        return self._path

    def __eq__(self, other):
        return isinstance(other, CustomPath) and self._path == other._path


@dataclass
class MyDataClassWithUnion(DataClassDictMixin):
    a: Union[int, str]
    b: Union[MyEnum, int]


@dataclass
class MyDataClassWithOptional(DataClassDictMixin):
    a: Optional[int] = None
    b: Optional[int] = None


@dataclass
class MyDataClassWithOptionalAndOmitNoneFlag(DataClassDictMixin):
    a: Optional[int] = None
    b: Optional[int] = None

    class Config(BaseConfig):
        code_generation_options = [TO_DICT_ADD_OMIT_NONE_FLAG]


class ThirdPartyType:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, ThirdPartyType) and self.value == other.value


@dataclass
class DataClassWithoutMixin:
    i: int


@dataclass
class SerializableTypeDataClass(SerializableType):
    a: int
    b: int

    def _serialize(self):
        return {"a": self.a + 1, "b": self.b + 1}

    @classmethod
    def _deserialize(cls, value):
        a = value.get("a") - 1
        b = value.get("b") - 1
        return cls(a, b)
