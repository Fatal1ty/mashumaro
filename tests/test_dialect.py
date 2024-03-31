import collections
import enum
import typing
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import (
    FrozenSet,
    Generic,
    List,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
)

import pytest
from typing_extensions import TypedDict

from mashumaro import DataClassDictMixin, pass_through
from mashumaro.config import ADD_DIALECT_SUPPORT, BaseConfig
from mashumaro.dialect import Dialect
from mashumaro.exceptions import BadDialect
from mashumaro.mixins.msgpack import DataClassMessagePackMixin
from mashumaro.mixins.msgpack import default_encoder as msgpack_encoder
from mashumaro.types import SerializationStrategy

from .conftest import add_unpack_method

T_Date = TypeVar("T_Date", bound=date)


class HexSerializationStrategy(SerializationStrategy):
    def serialize(self, value: int) -> str:
        return hex(value)

    def deserialize(self, value: str) -> int:
        return int(value, 16)


class OrdinalDialect(Dialect):
    serialization_strategy = {
        date: {
            "serialize": date.toordinal,
            "deserialize": date.fromordinal,
        },
        int: HexSerializationStrategy(),
    }


class FormattedDialect(Dialect):
    serialization_strategy = {
        date: {
            "serialize": lambda dt: dt.strftime("%Y/%m/%d"),
            "deserialize": lambda s: datetime.strptime(s, "%Y/%m/%d").date(),
        },
        int: HexSerializationStrategy(),
    }


class ISODialect(Dialect):
    serialization_strategy = {
        date: {
            "serialize": date.isoformat,
            "deserialize": date.fromisoformat,
        },
        int: HexSerializationStrategy(),
    }


class EmptyDialect(Dialect):
    pass


class OmitNoneDialect(Dialect):
    omit_none = True


class NotOmitNoneDialect(Dialect):
    omit_none = False


class OmitDefaultDialect(Dialect):
    omit_default = True


class NotOmitDefaultDialect(Dialect):
    omit_default = False


@dataclass
class DataClassWithoutDialects(DataClassDictMixin):
    dt: date
    i: int


@dataclass
class DataClassWithDefaultDialect(DataClassDictMixin):
    dt: date
    i: int

    class Config(BaseConfig):
        dialect = OrdinalDialect


@dataclass
class DataClassWithDialectSupport(DataClassDictMixin):
    dt: date
    i: int

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]


@dataclass
class BaseEntityWithDialect(DataClassDictMixin):
    class Config:
        code_generation_options = [ADD_DIALECT_SUPPORT]


@dataclass
class Entity1(BaseEntityWithDialect):
    dt1: date


@dataclass
class Entity2(BaseEntityWithDialect):
    dt2: date


@dataclass
class DataClassWithDialectSupportAndDefaultDialect(DataClassDictMixin):
    dt: date
    i: int

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]
        dialect = FormattedDialect


@dataclass
class GenericDataClassWithoutDialects(Generic[T_Date], DataClassDictMixin):
    dt: T_Date
    i: int


@dataclass
class GenericDataClassWithDefaultDialect(Generic[T_Date], DataClassDictMixin):
    dt: T_Date
    i: int

    class Config(BaseConfig):
        dialect = OrdinalDialect


@dataclass
class GenericDataClassWithDialectSupport(Generic[T_Date], DataClassDictMixin):
    dt: T_Date
    i: int

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]


@dataclass
class GenericDataClassWithDialectSupportAndDefaultDialect(
    Generic[T_Date], DataClassDictMixin
):
    dt: T_Date
    i: int

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]
        dialect = FormattedDialect


class MyNamedTuple(NamedTuple):
    x: DataClassWithDialectSupport = DataClassWithDialectSupport(
        dt=date(2022, 1, 1),
        i=999,
    )
    y: DataClassWithoutDialects = DataClassWithoutDialects(
        dt=date(2022, 1, 1),
        i=999,
    )


class MyTypedDict(TypedDict):
    x: DataClassWithDialectSupport
    y: DataClassWithoutDialects


@dataclass
class DataClassWithNamedTupleWithDialectSupport(DataClassDictMixin):
    x: MyNamedTuple

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]


@dataclass
class DataClassWithNamedTupleWithoutDialectSupport(DataClassDictMixin):
    x: MyNamedTuple


@dataclass
class DataClassWithTypedDictWithDialectSupport(DataClassDictMixin):
    x: MyTypedDict

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]


@dataclass
class DataClassWithTypedDictWithoutDialectSupport(DataClassDictMixin):
    x: MyTypedDict


@dataclass
class DataClassWithUnionWithDialectSupport(DataClassDictMixin):
    x: List[Union[DataClassWithDialectSupport, DataClassWithoutDialects]]

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]


@dataclass
class MessagePackDataClass(DataClassMessagePackMixin):
    b_1: bytes
    b_2: bytearray
    dep_1: DataClassWithoutDialects
    dep_2: GenericDataClassWithoutDialects[date]


@dataclass
class DataClassWithOptionalAndOmitNoneDialect(DataClassDictMixin):
    x: Optional[int] = None

    class Config(BaseConfig):
        dialect = OmitNoneDialect


@dataclass
class DataClassWithOptionalAndOmitNoneDialectAndOmitNoneFalse(
    DataClassDictMixin
):
    x: Optional[int] = None

    class Config(BaseConfig):
        dialect = OmitNoneDialect
        omit_none = False


@dataclass
class DataClassWithOptionalAndNotOmitNoneDialectAndOmitNoneTrue(
    DataClassDictMixin
):
    x: Optional[int] = None

    class Config(BaseConfig):
        dialect = NotOmitNoneDialect
        omit_none = True


@dataclass
class DataClassWithOptionalAndEmptyDialect(DataClassDictMixin):
    x: Optional[int] = None

    class Config(BaseConfig):
        dialect = EmptyDialect
        omit_none = True


@dataclass
class DataClassWithOptionalAndDialectSupport(DataClassDictMixin):
    x: Optional[int] = None

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]


class MyStrEnum(str, enum.Enum):
    VAL1 = "val1"
    VAL2 = "val2"


@dataclass
class DataClassWithDefaultAndOmitDefaultDialect(DataClassDictMixin):
    a: int = 42
    b: float = 3.14
    c: str = "foo"
    d: bool = False
    e: None = None
    f: type(None) = None
    g: Tuple[int] = (1, 2, 3)
    h: MyNamedTuple = field(default_factory=lambda: MyNamedTuple())
    i: List[int] = field(default_factory=list)
    j: List[int] = field(default_factory=lambda: [1, 2, 3])
    k: Set[int] = field(default_factory=set)
    l: Set[int] = field(default_factory=lambda: {1, 2, 3})
    m: FrozenSet[int] = field(default_factory=frozenset)
    n: FrozenSet[int] = field(default_factory=lambda: frozenset({1, 2, 3}))
    o: str = MyStrEnum.VAL1

    class Config(BaseConfig):
        dialect = OmitDefaultDialect


@dataclass
class DataClassWithDefaultAndOmitDefaultDialectAndOmitDefaultFalse(
    DataClassDictMixin
):
    a: int = 42
    b: float = 3.14
    c: str = "foo"
    d: bool = False
    e: None = None
    f: type(None) = None
    g: Tuple[int] = (1, 2, 3)
    h: MyNamedTuple = field(default_factory=lambda: MyNamedTuple())
    i: List[int] = field(default_factory=list)
    j: List[int] = field(default_factory=lambda: [1, 2, 3])
    k: Set[int] = field(default_factory=set)
    l: Set[int] = field(default_factory=lambda: {1, 2, 3})
    m: FrozenSet[int] = field(default_factory=frozenset)
    n: FrozenSet[int] = field(default_factory=lambda: frozenset({1, 2, 3}))
    o: str = MyStrEnum.VAL1

    class Config(BaseConfig):
        dialect = OmitDefaultDialect
        omit_default = False


@dataclass
class DataClassWithDefaultAndNotOmitDefaultDialectAndOmitDefaultTrue(
    DataClassDictMixin
):
    a: int = 42
    b: float = 3.14
    c: str = "foo"
    d: bool = False
    e: None = None
    f: type(None) = None
    g: Tuple[int] = (1, 2, 3)
    h: MyNamedTuple = field(default_factory=lambda: MyNamedTuple())
    i: List[int] = field(default_factory=list)
    j: List[int] = field(default_factory=lambda: [1, 2, 3])
    k: Set[int] = field(default_factory=set)
    l: Set[int] = field(default_factory=lambda: {1, 2, 3})
    m: FrozenSet[int] = field(default_factory=frozenset)
    n: FrozenSet[int] = field(default_factory=lambda: frozenset({1, 2, 3}))
    o: str = MyStrEnum.VAL1

    class Config(BaseConfig):
        dialect = NotOmitDefaultDialect
        omit_default = True


@dataclass
class DataClassWithDefaultAndEmptyDialect(DataClassDictMixin):
    a: int = 42
    b: float = 3.14
    c: str = "foo"
    d: bool = False
    e: None = None
    f: type(None) = None
    g: Tuple[int] = (1, 2, 3)
    h: MyNamedTuple = field(default_factory=lambda: MyNamedTuple())
    i: List[int] = field(default_factory=list)
    j: List[int] = field(default_factory=lambda: [1, 2, 3])
    k: Set[int] = field(default_factory=set)
    l: Set[int] = field(default_factory=lambda: {1, 2, 3})
    m: FrozenSet[int] = field(default_factory=frozenset)
    n: FrozenSet[int] = field(default_factory=lambda: frozenset({1, 2, 3}))
    o: str = MyStrEnum.VAL1

    class Config(BaseConfig):
        dialect = EmptyDialect
        omit_default = True


@dataclass
class DataClassWithDefaultAndDialectSupport(DataClassDictMixin):
    a: int = 42
    b: float = 3.14
    c: str = "foo"
    d: bool = False
    e: None = None
    f: type(None) = None
    g: Tuple[int] = (1, 2, 3)
    h: MyNamedTuple = field(default_factory=lambda: MyNamedTuple())
    i: List[int] = field(default_factory=list)
    j: List[int] = field(default_factory=lambda: [1, 2, 3])
    k: Set[int] = field(default_factory=set)
    l: Set[int] = field(default_factory=lambda: {1, 2, 3})
    m: FrozenSet[int] = field(default_factory=frozenset)
    n: FrozenSet[int] = field(default_factory=lambda: frozenset({1, 2, 3}))
    o: str = MyStrEnum.VAL1

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]


def test_default_dialect():
    dt = date.today()
    ordinal = dt.toordinal()
    obj = DataClassWithDefaultDialect(dt, 255)
    assert obj.to_dict() == {"dt": ordinal, "i": "0xff"}
    assert (
        DataClassWithDefaultDialect.from_dict({"dt": ordinal, "i": "0xff"})
        == obj
    )
    with pytest.raises(TypeError):
        obj.to_dict(dialect=OrdinalDialect)


def test_dialect():
    dt = date.today()
    ordinal = dt.toordinal()
    obj = DataClassWithDialectSupport(dt, 255)
    assert obj.to_dict(dialect=OrdinalDialect) == {"dt": ordinal, "i": "0xff"}
    assert (
        DataClassWithDialectSupport.from_dict(
            {"dt": ordinal, "i": "0xff"}, dialect=OrdinalDialect
        )
        == obj
    )


def test_dialect_with_default():
    dt = date.today()
    ordinal = dt.toordinal()
    formatted = dt.strftime("%Y/%m/%d")
    obj = DataClassWithDialectSupportAndDefaultDialect(dt, 255)
    assert obj.to_dict() == {"dt": formatted, "i": "0xff"}
    assert (
        DataClassWithDialectSupportAndDefaultDialect.from_dict(
            {"dt": formatted, "i": "0xff"}
        )
        == obj
    )
    assert obj.to_dict(dialect=None) == {"dt": formatted, "i": "0xff"}
    assert (
        DataClassWithDialectSupportAndDefaultDialect.from_dict(
            {"dt": formatted, "i": "0xff"}, dialect=None
        )
        == obj
    )
    assert obj.to_dict(dialect=OrdinalDialect) == {"dt": ordinal, "i": "0xff"}
    assert (
        DataClassWithDialectSupportAndDefaultDialect.from_dict(
            {"dt": ordinal, "i": "0xff"}, dialect=OrdinalDialect
        )
        == obj
    )


def test_bad_default_dialect():
    with pytest.raises(BadDialect):

        @dataclass
        class _(DataClassDictMixin):
            dt: date

            class Config(BaseConfig):
                dialect = int

    with add_unpack_method:
        with pytest.raises(BadDialect):

            @dataclass
            class _(DataClassDictMixin):
                dt: date

                class Config(BaseConfig):
                    dialect = int


def test_bad_dialect():
    dt = date.today()
    ordinal = dt.toordinal()
    obj = DataClassWithDialectSupport(dt, 255)
    with pytest.raises(BadDialect):
        DataClassWithDialectSupport.from_dict(
            {"dt": ordinal, "i": "0xff"}, dialect=int
        )
    with pytest.raises(BadDialect):
        obj.to_dict(dialect=int)


def test_inner_without_dialects():
    @dataclass
    class DataClass(DataClassDictMixin):
        dt: date
        inner: DataClassWithoutDialects
        inners: List[DataClassWithoutDialects]
        i: int

        class Config(BaseConfig):
            code_generation_options = [ADD_DIALECT_SUPPORT]
            dialect = FormattedDialect

    dt = date.today()
    formatted = dt.strftime("%Y/%m/%d")
    ordinal = dt.toordinal()
    iso = dt.isoformat()
    obj = DataClass(
        dt=dt,
        inner=DataClassWithoutDialects(dt, 255),
        inners=[DataClassWithoutDialects(dt, 255)],
        i=255,
    )
    assert obj.to_dict() == {
        "dt": formatted,
        "inner": {"dt": iso, "i": 255},
        "inners": [{"dt": iso, "i": 255}],
        "i": "0xff",
    }
    assert obj.to_dict(dialect=OrdinalDialect) == {
        "dt": ordinal,
        "inner": {"dt": iso, "i": 255},
        "inners": [{"dt": iso, "i": 255}],
        "i": "0xff",
    }
    assert (
        DataClass.from_dict(
            {
                "dt": formatted,
                "inner": {"dt": iso, "i": 255},
                "inners": [{"dt": iso, "i": 255}],
                "i": "0xff",
            }
        )
        == obj
    )
    assert (
        DataClass.from_dict(
            {
                "dt": ordinal,
                "inner": {"dt": iso, "i": 255},
                "inners": [{"dt": iso, "i": 255}],
                "i": "0xff",
            },
            dialect=OrdinalDialect,
        )
        == obj
    )


def test_inner_with_default_dialect():
    @dataclass
    class DataClass(DataClassDictMixin):
        dt: date
        inner: DataClassWithDefaultDialect
        inners: List[DataClassWithDefaultDialect]
        i: int

        class Config(BaseConfig):
            code_generation_options = [ADD_DIALECT_SUPPORT]
            dialect = FormattedDialect

    dt = date.today()
    formatted = dt.strftime("%Y/%m/%d")
    ordinal = dt.toordinal()
    iso = dt.isoformat()
    obj = DataClass(
        dt=dt,
        inner=DataClassWithDefaultDialect(dt, 255),
        inners=[DataClassWithDefaultDialect(dt, 255)],
        i=255,
    )
    assert obj.to_dict() == {
        "dt": formatted,
        "inner": {"dt": ordinal, "i": "0xff"},
        "inners": [{"dt": ordinal, "i": "0xff"}],
        "i": "0xff",
    }
    assert obj.to_dict(dialect=ISODialect) == {
        "dt": iso,
        "inner": {"dt": ordinal, "i": "0xff"},
        "inners": [{"dt": ordinal, "i": "0xff"}],
        "i": "0xff",
    }
    assert (
        DataClass.from_dict(
            {
                "dt": formatted,
                "inner": {"dt": ordinal, "i": "0xff"},
                "inners": [{"dt": ordinal, "i": "0xff"}],
                "i": "0xff",
            }
        )
        == obj
    )
    assert (
        DataClass.from_dict(
            {
                "dt": iso,
                "inner": {"dt": ordinal, "i": "0xff"},
                "inners": [{"dt": ordinal, "i": "0xff"}],
                "i": "0xff",
            },
            dialect=ISODialect,
        )
        == obj
    )


def test_inner_with_dialect_support():
    @dataclass
    class DataClass(DataClassDictMixin):
        dt: date
        inner: DataClassWithDialectSupport
        inners: List[DataClassWithDialectSupport]
        i: int

        class Config(BaseConfig):
            code_generation_options = [ADD_DIALECT_SUPPORT]
            dialect = FormattedDialect

    dt = date.today()
    ordinal = dt.toordinal()
    formatted = dt.strftime("%Y/%m/%d")
    iso = dt.isoformat()
    obj = DataClass(
        dt=dt,
        inner=DataClassWithDialectSupport(dt, 255),
        inners=[DataClassWithDialectSupport(dt, 255)],
        i=255,
    )
    assert obj.to_dict() == {
        "dt": formatted,
        "inner": {"dt": iso, "i": 255},
        "inners": [{"dt": iso, "i": 255}],
        "i": "0xff",
    }
    assert obj.to_dict(dialect=OrdinalDialect) == {
        "dt": ordinal,
        "inner": {"dt": ordinal, "i": "0xff"},
        "inners": [{"dt": ordinal, "i": "0xff"}],
        "i": "0xff",
    }
    assert (
        DataClass.from_dict(
            {
                "dt": formatted,
                "inner": {"dt": iso, "i": 255},
                "inners": [{"dt": iso, "i": 255}],
                "i": "0xff",
            }
        )
        == obj
    )
    assert (
        DataClass.from_dict(
            {
                "dt": ordinal,
                "inner": {"dt": ordinal, "i": "0xff"},
                "inners": [{"dt": ordinal, "i": "0xff"}],
                "i": "0xff",
            },
            dialect=OrdinalDialect,
        )
        == obj
    )


def test_inner_with_dialect_support_and_default():
    @dataclass
    class DataClass(DataClassDictMixin):
        dt: date
        inner: DataClassWithDialectSupportAndDefaultDialect
        inners: List[DataClassWithDialectSupportAndDefaultDialect]
        i: int

        class Config(BaseConfig):
            code_generation_options = [ADD_DIALECT_SUPPORT]
            dialect = FormattedDialect

    dt = date.today()
    formatted = dt.strftime("%Y/%m/%d")
    iso = dt.isoformat()
    obj = DataClass(
        dt=dt,
        inner=DataClassWithDialectSupportAndDefaultDialect(dt, 255),
        inners=[DataClassWithDialectSupportAndDefaultDialect(dt, 255)],
        i=255,
    )
    assert obj.to_dict() == {
        "dt": formatted,
        "inner": {"dt": formatted, "i": "0xff"},
        "inners": [{"dt": formatted, "i": "0xff"}],
        "i": "0xff",
    }
    assert obj.to_dict(dialect=ISODialect) == {
        "dt": iso,
        "inner": {"dt": iso, "i": "0xff"},
        "inners": [{"dt": iso, "i": "0xff"}],
        "i": "0xff",
    }
    assert (
        DataClass.from_dict(
            {
                "dt": formatted,
                "inner": {"dt": formatted, "i": "0xff"},
                "inners": [{"dt": formatted, "i": "0xff"}],
                "i": "0xff",
            }
        )
        == obj
    )
    assert (
        DataClass.from_dict(
            {
                "dt": iso,
                "inner": {"dt": iso, "i": "0xff"},
                "inners": [{"dt": iso, "i": "0xff"}],
                "i": "0xff",
            },
            dialect=ISODialect,
        )
        == obj
    )


def test_generic_without_dialects():
    @dataclass
    class DataClass(DataClassDictMixin):
        dt: date
        inner: GenericDataClassWithoutDialects[date]
        inners: List[GenericDataClassWithoutDialects[date]]
        i: int

        class Config(BaseConfig):
            code_generation_options = [ADD_DIALECT_SUPPORT]
            dialect = FormattedDialect

    dt = date.today()
    formatted = dt.strftime("%Y/%m/%d")
    ordinal = dt.toordinal()
    iso = dt.isoformat()
    obj = DataClass(
        dt=dt,
        inner=GenericDataClassWithoutDialects(dt, 255),
        inners=[GenericDataClassWithoutDialects(dt, 255)],
        i=255,
    )
    assert obj.to_dict() == {
        "dt": formatted,
        "inner": {"dt": iso, "i": 255},
        "inners": [{"dt": iso, "i": 255}],
        "i": "0xff",
    }
    assert obj.to_dict(dialect=OrdinalDialect) == {
        "dt": ordinal,
        "inner": {"dt": iso, "i": 255},
        "inners": [{"dt": iso, "i": 255}],
        "i": "0xff",
    }
    assert (
        DataClass.from_dict(
            {
                "dt": formatted,
                "inner": {"dt": iso, "i": 255},
                "inners": [{"dt": iso, "i": 255}],
                "i": "0xff",
            }
        )
        == obj
    )
    assert (
        DataClass.from_dict(
            {
                "dt": ordinal,
                "inner": {"dt": iso, "i": 255},
                "inners": [{"dt": iso, "i": 255}],
                "i": "0xff",
            },
            dialect=OrdinalDialect,
        )
        == obj
    )


def test_generic_with_default_dialect():
    @dataclass
    class DataClass(DataClassDictMixin):
        dt: date
        inner: GenericDataClassWithDefaultDialect[date]
        inners: List[GenericDataClassWithDefaultDialect[date]]
        i: int

        class Config(BaseConfig):
            code_generation_options = [ADD_DIALECT_SUPPORT]
            dialect = FormattedDialect

    dt = date.today()
    formatted = dt.strftime("%Y/%m/%d")
    ordinal = dt.toordinal()
    iso = dt.isoformat()
    obj = DataClass(
        dt=dt,
        inner=GenericDataClassWithDefaultDialect(dt, 255),
        inners=[GenericDataClassWithDefaultDialect(dt, 255)],
        i=255,
    )
    assert obj.to_dict() == {
        "dt": formatted,
        "inner": {"dt": ordinal, "i": "0xff"},
        "inners": [{"dt": ordinal, "i": "0xff"}],
        "i": "0xff",
    }
    assert obj.to_dict(dialect=ISODialect) == {
        "dt": iso,
        "inner": {"dt": ordinal, "i": "0xff"},
        "inners": [{"dt": ordinal, "i": "0xff"}],
        "i": "0xff",
    }
    assert (
        DataClass.from_dict(
            {
                "dt": formatted,
                "inner": {"dt": ordinal, "i": "0xff"},
                "inners": [{"dt": ordinal, "i": "0xff"}],
                "i": "0xff",
            }
        )
        == obj
    )
    assert (
        DataClass.from_dict(
            {
                "dt": iso,
                "inner": {"dt": ordinal, "i": "0xff"},
                "inners": [{"dt": ordinal, "i": "0xff"}],
                "i": "0xff",
            },
            dialect=ISODialect,
        )
        == obj
    )


def test_generic_with_dialect_support():
    @dataclass
    class DataClass(DataClassDictMixin):
        dt: date
        inner: GenericDataClassWithDialectSupport[date]
        inners: List[GenericDataClassWithDialectSupport[date]]
        i: int

        class Config(BaseConfig):
            code_generation_options = [ADD_DIALECT_SUPPORT]
            dialect = FormattedDialect

    dt = date.today()
    ordinal = dt.toordinal()
    formatted = dt.strftime("%Y/%m/%d")
    iso = dt.isoformat()
    obj = DataClass(
        dt=dt,
        inner=GenericDataClassWithDialectSupport(dt, 255),
        inners=[GenericDataClassWithDialectSupport(dt, 255)],
        i=255,
    )
    assert obj.to_dict() == {
        "dt": formatted,
        "inner": {"dt": iso, "i": 255},
        "inners": [{"dt": iso, "i": 255}],
        "i": "0xff",
    }
    assert obj.to_dict(dialect=OrdinalDialect) == {
        "dt": ordinal,
        "inner": {"dt": ordinal, "i": "0xff"},
        "inners": [{"dt": ordinal, "i": "0xff"}],
        "i": "0xff",
    }
    assert (
        DataClass.from_dict(
            {
                "dt": formatted,
                "inner": {"dt": iso, "i": 255},
                "inners": [{"dt": iso, "i": 255}],
                "i": "0xff",
            }
        )
        == obj
    )
    assert (
        DataClass.from_dict(
            {
                "dt": ordinal,
                "inner": {"dt": ordinal, "i": "0xff"},
                "inners": [{"dt": ordinal, "i": "0xff"}],
                "i": "0xff",
            },
            dialect=OrdinalDialect,
        )
        == obj
    )


def test_generic_with_dialect_support_and_default():
    @dataclass
    class DataClass(DataClassDictMixin):
        dt: date
        inner: GenericDataClassWithDialectSupportAndDefaultDialect[date]
        inners: List[GenericDataClassWithDialectSupportAndDefaultDialect[date]]
        i: int

        class Config(BaseConfig):
            code_generation_options = [ADD_DIALECT_SUPPORT]
            dialect = FormattedDialect

    dt = date.today()
    formatted = dt.strftime("%Y/%m/%d")
    iso = dt.isoformat()
    obj = DataClass(
        dt=dt,
        inner=GenericDataClassWithDialectSupportAndDefaultDialect(dt, 255),
        inners=[GenericDataClassWithDialectSupportAndDefaultDialect(dt, 255)],
        i=255,
    )
    assert obj.to_dict() == {
        "dt": formatted,
        "inner": {"dt": formatted, "i": "0xff"},
        "inners": [{"dt": formatted, "i": "0xff"}],
        "i": "0xff",
    }
    assert obj.to_dict(dialect=ISODialect) == {
        "dt": iso,
        "inner": {"dt": iso, "i": "0xff"},
        "inners": [{"dt": iso, "i": "0xff"}],
        "i": "0xff",
    }
    assert (
        DataClass.from_dict(
            {
                "dt": formatted,
                "inner": {"dt": formatted, "i": "0xff"},
                "inners": [{"dt": formatted, "i": "0xff"}],
                "i": "0xff",
            }
        )
        == obj
    )
    assert (
        DataClass.from_dict(
            {
                "dt": iso,
                "inner": {"dt": iso, "i": "0xff"},
                "inners": [{"dt": iso, "i": "0xff"}],
                "i": "0xff",
            },
            dialect=ISODialect,
        )
        == obj
    )


def test_debug_true_option_with_dialect(mocker):
    mocked_print = mocker.patch("builtins.print")

    @dataclass
    class DataClass(DataClassDictMixin):
        dt: date

        class Config(BaseConfig):
            debug = True
            code_generation_options = [ADD_DIALECT_SUPPORT]

    DataClass(date.today()).to_dict(dialect=FormattedDialect)
    mocked_print.assert_called()
    assert mocked_print.call_count == 6


def test_dialect_with_named_tuple_with_dialect_support():
    dt = date.today()
    ordinal = dt.toordinal()
    iso = dt.isoformat()
    obj = DataClassWithNamedTupleWithDialectSupport(
        x=MyNamedTuple(
            x=DataClassWithDialectSupport(dt, 255),
            y=DataClassWithoutDialects(dt, 255),
        )
    )
    dumped = {"x": [{"dt": ordinal, "i": "0xff"}, {"dt": iso, "i": 255}]}
    assert obj.to_dict(dialect=OrdinalDialect) == dumped
    assert (
        DataClassWithNamedTupleWithDialectSupport.from_dict(
            dumped, dialect=OrdinalDialect
        )
        == obj
    )


def test_dialect_with_named_tuple_without_dialect_support():
    dt = date.today()
    iso = dt.isoformat()
    obj = DataClassWithNamedTupleWithoutDialectSupport(
        x=MyNamedTuple(
            x=DataClassWithDialectSupport(dt, 255),
            y=DataClassWithoutDialects(dt, 255),
        )
    )
    dumped = {"x": [{"dt": iso, "i": 255}, {"dt": iso, "i": 255}]}
    assert obj.to_dict() == dumped
    assert (
        DataClassWithNamedTupleWithoutDialectSupport.from_dict(dumped) == obj
    )


def test_dialect_with_typed_dict_with_dialect_support():
    dt = date.today()
    ordinal = dt.toordinal()
    iso = dt.isoformat()
    obj = DataClassWithTypedDictWithDialectSupport(
        x=MyTypedDict(
            x=DataClassWithDialectSupport(dt, 255),
            y=DataClassWithoutDialects(dt, 255),
        )
    )
    dumped = {
        "x": {"x": {"dt": ordinal, "i": "0xff"}, "y": {"dt": iso, "i": 255}}
    }
    assert obj.to_dict(dialect=OrdinalDialect) == dumped
    assert (
        DataClassWithTypedDictWithDialectSupport.from_dict(
            dumped, dialect=OrdinalDialect
        )
        == obj
    )


def test_dialect_with_typed_dict_without_dialect_support():
    dt = date.today()
    iso = dt.isoformat()
    obj = DataClassWithTypedDictWithoutDialectSupport(
        x=MyTypedDict(
            x=DataClassWithDialectSupport(dt, 255),
            y=DataClassWithoutDialects(dt, 255),
        )
    )
    dumped = {"x": {"x": {"dt": iso, "i": 255}, "y": {"dt": iso, "i": 255}}}
    assert obj.to_dict() == dumped
    assert DataClassWithTypedDictWithoutDialectSupport.from_dict(dumped) == obj


def test_dialect_with_union_with_dialect_support():
    dt = date.today()
    ordinal = dt.toordinal()
    iso = dt.isoformat()
    obj = DataClassWithUnionWithDialectSupport(
        x=[
            DataClassWithDialectSupport(dt, 255),
            DataClassWithoutDialects(dt, 255),
        ]
    )
    dumped = {"x": [{"dt": ordinal, "i": "0xff"}, {"dt": iso, "i": 255}]}
    assert obj.to_dict(dialect=OrdinalDialect) == dumped
    assert (
        DataClassWithUnionWithDialectSupport.from_dict(
            dumped, dialect=OrdinalDialect
        )
        == obj
    )


def test_dialect_with_inheritance():
    dt = date.today()
    formatted = dt.strftime("%Y/%m/%d")
    entity1 = Entity1(dt)
    entity2 = Entity2(dt)

    assert (
        Entity1.from_dict({"dt1": formatted}, dialect=FormattedDialect)
        == entity1
    )
    assert (
        Entity2.from_dict({"dt2": formatted}, dialect=FormattedDialect)
        == entity2
    )
    assert entity1.to_dict(dialect=FormattedDialect) == {"dt1": formatted}
    assert entity2.to_dict(dialect=FormattedDialect) == {"dt2": formatted}


def test_msgpack_dialect_class_with_dependency_without_dialect():
    dt = date(2022, 6, 8)
    obj = MessagePackDataClass(
        b_1=b"123",
        b_2=bytearray([4, 5, 6]),
        dep_1=DataClassWithoutDialects(dt, 123),
        dep_2=GenericDataClassWithoutDialects(dt, 123),
    )
    d = {
        "b_1": b"123",
        "b_2": bytearray([4, 5, 6]),
        "dep_1": {"dt": "2022-06-08", "i": 123},
        "dep_2": {"dt": "2022-06-08", "i": 123},
    }
    encoded = msgpack_encoder(d)
    assert obj.to_msgpack() == encoded
    assert MessagePackDataClass.from_msgpack(encoded) == obj


def test_dataclass_omit_none_dialects():
    assert DataClassWithOptionalAndOmitNoneDialect().to_dict() == {}
    assert (
        DataClassWithOptionalAndOmitNoneDialectAndOmitNoneFalse().to_dict()
        == {}
    )
    assert (
        DataClassWithOptionalAndNotOmitNoneDialectAndOmitNoneTrue().to_dict()
        == {"x": None}
    )
    assert DataClassWithOptionalAndEmptyDialect().to_dict() == {}
    assert DataClassWithOptionalAndDialectSupport().to_dict() == {"x": None}
    assert (
        DataClassWithOptionalAndDialectSupport().to_dict(
            dialect=OmitNoneDialect
        )
        == {}
    )
    assert DataClassWithOptionalAndDialectSupport().to_dict(
        dialect=NotOmitNoneDialect
    ) == {"x": None}
    assert DataClassWithOptionalAndDialectSupport().to_dict(
        dialect=EmptyDialect
    ) == {"x": None}


def test_dataclass_omit_default_dialects():
    complete_dict = {
        "a": 42,
        "b": 3.14,
        "c": "foo",
        "d": False,
        "e": None,
        "f": None,
        "g": [1],
        "h": [{"dt": "2022-01-01", "i": 999}, {"dt": "2022-01-01", "i": 999}],
        "i": [],
        "j": [1, 2, 3],
        "k": [],
        "l": [1, 2, 3],
        "m": [],
        "n": [1, 2, 3],
        "o": MyStrEnum.VAL1,
    }
    assert DataClassWithDefaultAndOmitDefaultDialect().to_dict() == {}
    assert (
        DataClassWithDefaultAndOmitDefaultDialectAndOmitDefaultFalse().to_dict()
        == {}
    )
    assert (
        DataClassWithDefaultAndNotOmitDefaultDialectAndOmitDefaultTrue().to_dict()
        == complete_dict
    )
    assert DataClassWithDefaultAndEmptyDialect().to_dict() == {}
    assert DataClassWithDefaultAndDialectSupport().to_dict() == complete_dict
    assert (
        DataClassWithDefaultAndDialectSupport().to_dict(
            dialect=OmitDefaultDialect
        )
        == {}
    )
    assert (
        DataClassWithDefaultAndDialectSupport().to_dict(
            dialect=NotOmitDefaultDialect
        )
        == complete_dict
    )
    assert (
        DataClassWithDefaultAndDialectSupport().to_dict(dialect=EmptyDialect)
        == complete_dict
    )


def test_dialect_no_copy():
    class NoCopyDialect(Dialect):
        no_copy_collections = (list, dict, set)
        serialization_strategy = {int: {"serialize": pass_through}}

    @dataclass
    class DataClass(DataClassDictMixin):
        a: List[str]
        b: Set[str]
        c: typing.ChainMap[str, str]
        d: typing.OrderedDict[str, str]
        e: typing.Counter[str]
        f: typing.Dict[str, str]
        g: typing.Sequence[str]

        class Config(BaseConfig):
            dialect = NoCopyDialect

    obj = DataClass(
        a=["foo"],
        b={"foo"},
        c=collections.ChainMap({"foo": "bar"}),
        d=collections.OrderedDict({"foo": "bar"}),
        e=collections.Counter({"foo": 1}),
        f={"foo": "bar"},
        g=["foo"],
    )
    data = obj.to_dict()
    assert data["a"] is obj.a
    assert data["b"] is obj.b
    assert data["c"] is not obj.c
    assert data["d"] is not obj.d
    assert data["e"] is not obj.e
    assert data["f"] is obj.f
    assert data["g"] is not obj.g


def test_dialect_merge():
    class DialectA(Dialect):
        omit_none = True
        omit_default = True
        no_copy_collections = [set, dict]
        serialization_strategy = {
            date: {
                "serialize": date.toordinal,
                "deserialize": date.fromordinal,
            },
            int: HexSerializationStrategy(),
            float: {
                "serialize": pass_through,
                "deserialize": float,
            },
        }

    class DialectB(Dialect):
        omit_none = False
        omit_default = False
        no_copy_collections = [list]
        serialization_strategy = {
            date: pass_through,
            int: {
                "serialize": int,
                "deserialize": int,
            },
            float: {
                "serialize": float,
            },
        }

    DialectC = DialectA.merge(DialectB)
    assert DialectC.omit_none is False
    assert DialectC.omit_default is False
    assert DialectC.no_copy_collections == [list]
    assert DialectC.serialization_strategy == {
        date: pass_through,
        int: {
            "serialize": int,
            "deserialize": int,
        },
        float: {
            "serialize": float,
            "deserialize": float,
        },
    }
