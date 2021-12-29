from dataclasses import dataclass
from datetime import date, datetime
from typing import List

import pytest

from mashumaro import DataClassDictMixin
from mashumaro.config import ADD_DIALECT_SUPPORT, BaseConfig
from mashumaro.dialect import Dialect
from mashumaro.exceptions import BadDialect


class OrdinalDialect(Dialect):
    serialization_strategy = {
        date: {
            "serialize": date.toordinal,
            "deserialize": date.fromordinal,
        }
    }


class FormattedDialect(Dialect):
    serialization_strategy = {
        date: {
            "serialize": lambda dt: dt.strftime("%Y/%m/%d"),
            "deserialize": lambda s: datetime.strptime(s, "%Y/%m/%d").date(),
        }
    }


class ISODialect(Dialect):
    serialization_strategy = {
        date: {
            "serialize": date.isoformat,
            "deserialize": date.fromisoformat,
        }
    }


@dataclass
class DataClassWithoutDialects(DataClassDictMixin):
    dt: date


@dataclass
class DataClassWithDefaultDialect(DataClassDictMixin):
    dt: date

    class Config(BaseConfig):
        dialect = OrdinalDialect


@dataclass
class DataClassWithDialectSupport(DataClassDictMixin):
    dt: date

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]


@dataclass
class DataClassWithDialectSupportAndDefaultDialect(DataClassDictMixin):
    dt: date

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]
        dialect = FormattedDialect
        debug = True


# def test_default_dialect():
#     dt = date.today()
#     ordinal = dt.toordinal()
#     obj = DataClassWithDefaultDialect(dt)
#     assert obj.to_dict() == {"dt": ordinal}
#     assert DataClassWithDefaultDialect.from_dict({"dt": ordinal}) == obj
#     with pytest.raises(TypeError):
#         obj.to_dict(dialect=OrdinalDialect)
#     with pytest.raises(TypeError):
#         DataClassWithDefaultDialect.from_dict(
#             {"dt": ordinal}, dialect=OrdinalDialect
#         )


# def test_dialect():
#     dt = date.today()
#     ordinal = dt.toordinal()
#     obj = DataClassWithDialectSupport(dt)
#     assert obj.to_dict(dialect=OrdinalDialect) == {"dt": ordinal}
#     assert (
#         DataClassWithDialectSupport.from_dict(
#             {"dt": ordinal}, dialect=OrdinalDialect
#         )
#         == obj
#     )


def test_dialect_with_default():
    dt = date.today()
    ordinal = dt.toordinal()
    formatted = dt.strftime("%Y/%m/%d")
    obj = DataClassWithDialectSupportAndDefaultDialect(dt)
    assert obj.to_dict() == {"dt": formatted}
    assert (
        DataClassWithDialectSupportAndDefaultDialect.from_dict(
            {"dt": formatted}
        )
        == obj
    )
    assert obj.to_dict(dialect=None) == {"dt": formatted}
    assert (
        DataClassWithDialectSupportAndDefaultDialect.from_dict(
            {"dt": formatted}, dialect=None
        )
        == obj
    )
    assert obj.to_dict(dialect=OrdinalDialect) == {"dt": ordinal}
    assert (
        DataClassWithDialectSupportAndDefaultDialect.from_dict(
            {"dt": ordinal}, dialect=OrdinalDialect
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


def test_bad_dialect():
    dt = date.today()
    ordinal = dt.toordinal()
    obj = DataClassWithDialectSupport(dt)
    with pytest.raises(BadDialect):
        DataClassWithDialectSupport.from_dict({"dt": ordinal}, dialect=int)
    with pytest.raises(BadDialect):
        obj.to_dict(dialect=int)


def test_inner_without_dialects():
    @dataclass
    class DataClass(DataClassDictMixin):
        dt: date
        inner: DataClassWithoutDialects
        inners: List[DataClassWithoutDialects]

        class Config(BaseConfig):
            code_generation_options = [ADD_DIALECT_SUPPORT]
            dialect = FormattedDialect

    dt = date.today()
    formatted = dt.strftime("%Y/%m/%d")
    ordinal = dt.toordinal()
    iso = dt.isoformat()
    obj = DataClass(
        dt=dt,
        inner=DataClassWithoutDialects(dt),
        inners=[DataClassWithoutDialects(dt)],
    )
    assert obj.to_dict() == {
        "dt": formatted,
        "inner": {"dt": iso},
        "inners": [{"dt": iso}],
    }
    assert obj.to_dict(dialect=OrdinalDialect) == {
        "dt": ordinal,
        "inner": {"dt": iso},
        "inners": [{"dt": iso}],
    }
    assert (
        DataClass.from_dict(
            {
                "dt": formatted,
                "inner": {"dt": iso},
                "inners": [{"dt": iso}],
            }
        )
        == obj
    )
    assert (
        DataClass.from_dict(
            {"dt": ordinal, "inner": {"dt": iso}, "inners": [{"dt": iso}]},
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

        class Config(BaseConfig):
            code_generation_options = [ADD_DIALECT_SUPPORT]
            dialect = FormattedDialect

    dt = date.today()
    formatted = dt.strftime("%Y/%m/%d")
    ordinal = dt.toordinal()
    iso = dt.isoformat()
    obj = DataClass(
        dt=dt,
        inner=DataClassWithDefaultDialect(dt),
        inners=[DataClassWithDefaultDialect(dt)],
    )
    assert obj.to_dict() == {
        "dt": formatted,
        "inner": {"dt": ordinal},
        "inners": [{"dt": ordinal}],
    }
    assert obj.to_dict(dialect=ISODialect) == {
        "dt": iso,
        "inner": {"dt": ordinal},
        "inners": [{"dt": ordinal}],
    }
    assert (
        DataClass.from_dict(
            {
                "dt": formatted,
                "inner": {"dt": ordinal},
                "inners": [{"dt": ordinal}],
            }
        )
        == obj
    )
    assert (
        DataClass.from_dict(
            {"dt": iso, "inner": {"dt": ordinal}, "inners": [{"dt": ordinal}]},
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

        class Config(BaseConfig):
            code_generation_options = [ADD_DIALECT_SUPPORT]
            dialect = FormattedDialect

    dt = date.today()
    formatted = dt.strftime("%Y/%m/%d")
    iso = dt.isoformat()
    obj = DataClass(
        dt=dt,
        inner=DataClassWithDialectSupport(dt),
        inners=[DataClassWithDialectSupport(dt)],
    )
    assert obj.to_dict() == {
        "dt": formatted,
        "inner": {"dt": iso},
        "inners": [{"dt": iso}],
    }
    assert obj.to_dict(dialect=ISODialect) == {
        "dt": iso,
        "inner": {"dt": iso},
        "inners": [{"dt": iso}],
    }
    assert (
        DataClass.from_dict(
            {
                "dt": formatted,
                "inner": {"dt": iso},
                "inners": [{"dt": iso}],
            }
        )
        == obj
    )
    assert (
        DataClass.from_dict(
            {"dt": iso, "inner": {"dt": iso}, "inners": [{"dt": iso}]},
            dialect=ISODialect,
        )
        == obj
    )


def test_inner_with_dialect_support_and_default():
    @dataclass
    class DataClass(DataClassDictMixin):
        dt: date
        inner: DataClassWithDialectSupportAndDefaultDialect
        inners: List[DataClassWithDialectSupportAndDefaultDialect]

        class Config(BaseConfig):
            code_generation_options = [ADD_DIALECT_SUPPORT]
            dialect = FormattedDialect
            debug = False

    dt = date.today()
    formatted = dt.strftime("%Y/%m/%d")
    iso = dt.isoformat()
    obj = DataClass(
        dt=dt,
        inner=DataClassWithDialectSupportAndDefaultDialect(dt),
        inners=[DataClassWithDialectSupportAndDefaultDialect(dt)],
    )
    assert obj.to_dict() == {
        "dt": formatted,
        "inner": {"dt": formatted},
        "inners": [{"dt": formatted}],
    }
    assert obj.to_dict(dialect=ISODialect) == {
        "dt": iso,
        "inner": {"dt": iso},
        "inners": [{"dt": iso}],
    }
    assert (
        DataClass.from_dict(
            {
                "dt": formatted,
                "inner": {"dt": formatted},
                "inners": [{"dt": formatted}],
            }
        )
        == obj
    )
    assert (
        DataClass.from_dict(
            {"dt": iso, "inner": {"dt": iso}, "inners": [{"dt": iso}]},
            dialect=ISODialect,
        )
        == obj
    )
