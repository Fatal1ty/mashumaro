from dataclasses import dataclass
from datetime import date, datetime
from typing import Generic, List, NamedTuple, Optional, TypeVar, Union

import pytest
from typing_extensions import TypedDict

from mashumaro import DataClassDictMixin
from mashumaro.config import (
    ADD_DIALECT_SUPPORT,
    TO_DICT_ADD_OMIT_NONE_FLAG,
    BaseConfig,
)
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
    with pytest.raises(TypeError):
        DataClassWithDefaultDialect.from_dict(
            {"dt": ordinal, "i": "0xff"}, dialect=OrdinalDialect
        )


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
