from dataclasses import dataclass
from datetime import date, datetime, time
from typing import List, Optional

import tomli_w

from mashumaro.config import ADD_DIALECT_SUPPORT, BaseConfig

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

from mashumaro.dialect import Dialect
from mashumaro.mixins.toml import DataClassTOMLMixin

serialization_strategy = {
    datetime: {
        "serialize": lambda dt: dt.strftime("%Y/%m/%d/%H/%M/%S"),
        "deserialize": lambda s: datetime.strptime(s, "%Y/%m/%d/%H/%M/%S"),
    },
    date: {
        "serialize": date.toordinal,
        "deserialize": date.fromordinal,
    },
    time: {
        "serialize": lambda t: t.strftime("%H/%M/%S"),
        "deserialize": lambda s: datetime.strptime(s, "%H/%M/%S").time(),
    },
}


class MyDialect(Dialect):
    serialization_strategy = serialization_strategy


@dataclass
class InnerDataClassWithOptionalField(DataClassTOMLMixin):
    x: Optional[int] = None


def test_data_class_toml_mixin():
    assert DataClassTOMLMixin.from_toml("") is None
    assert DataClassTOMLMixin().to_toml() is None


def test_to_toml():
    @dataclass
    class DataClass(DataClassTOMLMixin):
        x: List[int]

    dumped = tomli_w.dumps({"x": [1, 2, 3]})
    assert DataClass([1, 2, 3]).to_toml() == dumped


def test_from_toml():
    @dataclass
    class DataClass(DataClassTOMLMixin):
        x: List[int]

    dumped = tomli_w.dumps({"x": [1, 2, 3]})
    assert DataClass.from_toml(dumped) == DataClass([1, 2, 3])


def test_toml_with_serialization_strategy():
    @dataclass
    class DataClass(DataClassTOMLMixin):
        datetime: List[datetime]
        date: List[date]
        time: List[time]

        class Config(BaseConfig):
            serialization_strategy = serialization_strategy

    _datetime = datetime(2022, 10, 12, 12, 54, 30)
    _date = date(2022, 10, 12)
    _time = time(12, 54, 30)
    _datetime_dumped = _datetime.strftime("%Y/%m/%d/%H/%M/%S")
    _date_dumped = _date.toordinal()
    _time_dumped = _time.strftime("%H/%M/%S")
    instance = DataClass([_datetime], [_date], [_time])
    dict_dumped = {
        "datetime": [_datetime_dumped],
        "date": [_date_dumped],
        "time": [_time_dumped],
    }
    toml_dumped = tomli_w.dumps(
        {
            "datetime": [_datetime_dumped],
            "date": [_date_dumped],
            "time": [_time_dumped],
        }
    )
    assert DataClass.from_dict(dict_dumped) == instance
    assert DataClass.from_toml(toml_dumped) == instance
    assert instance.to_dict() == dict_dumped
    assert instance.to_toml() == toml_dumped


def test_toml_with_dialect():
    @dataclass
    class DataClass(DataClassTOMLMixin):
        datetime: List[datetime]
        date: List[date]
        time: List[time]

        class Config(BaseConfig):
            dialect = MyDialect

    _datetime = datetime(2022, 10, 12, 12, 54, 30)
    _date = date(2022, 10, 12)
    _time = time(12, 54, 30)
    _datetime_dumped = _datetime.strftime("%Y/%m/%d/%H/%M/%S")
    _date_dumped = _date.toordinal()
    _time_dumped = _time.strftime("%H/%M/%S")
    instance = DataClass([_datetime], [_date], [_time])
    dict_dumped = {
        "datetime": [_datetime_dumped],
        "date": [_date_dumped],
        "time": [_time_dumped],
    }
    toml_dumped = tomli_w.dumps(
        {
            "datetime": [_datetime_dumped],
            "date": [_date_dumped],
            "time": [_time_dumped],
        }
    )
    assert DataClass.from_dict(dict_dumped) == instance
    assert DataClass.from_toml(toml_dumped) == instance
    assert instance.to_dict() == dict_dumped
    assert instance.to_toml() == toml_dumped


def test_toml_with_dialect_support():
    @dataclass
    class DataClass(DataClassTOMLMixin):
        datetime: List[datetime]
        date: List[date]
        time: List[time]

        class Config(BaseConfig):
            code_generation_options = [ADD_DIALECT_SUPPORT]

    _datetime = datetime(2022, 10, 12, 12, 54, 30)
    _date = date(2022, 10, 12)
    _time = time(12, 54, 30)
    _datetime_dumped = _datetime.strftime("%Y/%m/%d/%H/%M/%S")
    _date_dumped = _date.toordinal()
    _time_dumped = _time.strftime("%H/%M/%S")
    instance = DataClass([_datetime], [_date], [_time])
    dict_dumped = {
        "datetime": [_datetime.isoformat()],
        "date": [_date.isoformat()],
        "time": [_time.isoformat()],
    }
    dict_dumped_dialect = {
        "datetime": [_datetime_dumped],
        "date": [_date_dumped],
        "time": [_time_dumped],
    }
    toml_dumped = tomli_w.dumps(
        {"datetime": [_datetime], "date": [_date], "time": [_time]}
    )
    toml_dumped_dialect = tomli_w.dumps(
        {
            "datetime": [_datetime_dumped],
            "date": [_date_dumped],
            "time": [_time_dumped],
        }
    )
    assert DataClass.from_dict(dict_dumped) == instance
    assert (
        DataClass.from_dict(dict_dumped_dialect, dialect=MyDialect) == instance
    )
    assert DataClass.from_toml(toml_dumped) == instance
    assert (
        DataClass.from_toml(toml_dumped_dialect, dialect=MyDialect) == instance
    )
    assert instance.to_dict() == dict_dumped
    assert instance.to_dict(dialect=MyDialect) == dict_dumped_dialect
    assert instance.to_toml() == toml_dumped
    assert instance.to_toml(dialect=MyDialect) == toml_dumped_dialect


def test_toml_omit_none():
    @dataclass
    class DataClass(DataClassTOMLMixin):
        x: Optional[InnerDataClassWithOptionalField] = None
        y: Optional[int] = None

    obj = DataClass()
    assert obj.to_dict() == {"x": None, "y": None}
    assert obj.to_toml() == ""
    obj = DataClass(InnerDataClassWithOptionalField())
    assert obj.to_dict() == {"x": {"x": None}, "y": None}
    assert obj.to_toml() == "[x]\n"
    assert DataClass.from_toml("[x]\n") == obj
