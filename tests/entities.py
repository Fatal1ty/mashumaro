from collections import namedtuple
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum, Flag, IntEnum, IntFlag
from os import PathLike
from typing import Any, Generic, List, NewType, Optional, Union

try:
    from enum import StrEnum
except ImportError:  # pragma: no cover

    class StrEnum(str, Enum):
        pass


from typing_extensions import NamedTuple, ReadOnly, TypedDict, TypeVar

from mashumaro import DataClassDictMixin
from mashumaro.config import TO_DICT_ADD_OMIT_NONE_FLAG, BaseConfig
from mashumaro.types import GenericSerializableType, SerializableType

T = TypeVar("T")
TAny = TypeVar("TAny", bound=Any)
TInt = TypeVar("TInt", bound=int)
TDefaultInt = TypeVar("TDefaultInt", default=int)
TIntStr = TypeVar("TIntStr", int, str)
T_Optional_int = TypeVar("T_Optional_int", bound=Optional[int])


class MyEnum(Enum):
    a = "letter a"
    b = "letter b"


class MyStrEnum(str, Enum):
    a = "letter a"
    b = "letter b"


class MyNativeStrEnum(StrEnum):
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


@dataclass(frozen=True)
class MyFrozenDataClass:
    x: int


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


class GenericSerializableList(Generic[T], GenericSerializableType):
    def __init__(self, value: List[T]):
        self.value = value

    def _serialize(self, types):
        if types[0] == int:
            return [v + 2 for v in self.value]
        elif types[0] == str:
            return [f"_{v}" for v in self.value]

    @classmethod
    def _deserialize(cls, value, types):
        if types[0] == int:
            return GenericSerializableList([int(v) - 2 for v in value])
        elif types[0] == str:
            return GenericSerializableList([v[1:] for v in value])

    def __eq__(self, other):
        return self.value == other.value


class GenericSerializableWrapper(Generic[T], GenericSerializableType):
    def __init__(self, value: T):
        self.value = value

    def _serialize(self, types):
        if types[0] == date:
            return self.value.isoformat()

    @classmethod
    def _deserialize(cls, value, types):
        if types[0] == date:
            return GenericSerializableWrapper(date.fromisoformat(value))

    def __eq__(self, other):
        return self.value == other.value


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


@dataclass
class GenericSerializableTypeDataClass(GenericSerializableType):
    a: int
    b: int

    def _serialize(self, types):
        return {"a": self.a + 1, "b": self.b + 1}

    @classmethod
    def _deserialize(cls, value, types):
        a = value.get("a") - 1
        b = value.get("b") - 1
        return cls(a, b)


@dataclass
class MyGenericDataClass(Generic[T], DataClassDictMixin):
    x: T


class MyGenericList(List[T]):
    pass


class SerializableTypeGenericList(Generic[T], SerializableType):
    def __init__(self, value: List[T]):
        self.value = value

    def _serialize(self):
        return self.value

    @classmethod
    def _deserialize(cls, value):
        return SerializableTypeGenericList(value)

    def __eq__(self, other):
        return self.value == other.value


TMyDataClass = TypeVar("TMyDataClass", bound=MyDataClass)


class TypedDictRequiredKeys(TypedDict):
    int: int
    float: float


class TypedDictOptionalKeys(TypedDict, total=False):
    int: int
    float: float


class TypedDictRequiredAndOptionalKeys(TypedDictRequiredKeys, total=False):
    str: str


class TypedDictRequiredKeysWithOptional(TypedDict):
    x: Optional[int]
    y: int


class TypedDictOptionalKeysWithOptional(TypedDict, total=False):
    x: Optional[int]
    y: float


class TypedDictWithReadOnly(TypedDict):
    x: ReadOnly[int]


class GenericTypedDict(TypedDict, Generic[T]):
    x: T
    y: int


class MyNamedTuple(NamedTuple):
    i: int
    f: float


class MyNamedTupleWithDefaults(NamedTuple):
    i: int = 1
    f: float = 2.0


class MyNamedTupleWithOptional(NamedTuple):
    i: Optional[int]
    f: int


MyUntypedNamedTuple = namedtuple("MyUntypedNamedTuple", ("i", "f"))


MyUntypedNamedTupleWithDefaults = namedtuple(
    "MyUntypedNamedTupleWithDefaults",
    ("i", "f"),
    defaults=(1, 2.0),
)


class GenericNamedTuple(NamedTuple, Generic[T]):
    x: T
    y: int


MyDatetimeNewType = NewType("MyDatetimeNewType", datetime)
