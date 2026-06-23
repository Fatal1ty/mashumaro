from dataclasses import dataclass
from datetime import date, datetime, time
from typing import List
from uuid import UUID, uuid4

import yamlrocks

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig
from mashumaro.dialect import Dialect
from mashumaro.mixins.yamlrocks import DataClassYAMLRocksMixin

serialization_strategy = {
    datetime: {
        "serialize": lambda dt: dt.strftime("%Y/%m/%d/%H/%M/%S"),
        "deserialize": lambda s: datetime.strptime(s, "%Y/%m/%d/%H/%M/%S"),
    },
    date: {"serialize": date.toordinal, "deserialize": date.fromordinal},
    time: {
        "serialize": lambda t: t.strftime("%H/%M/%S"),
        "deserialize": lambda s: datetime.strptime(s, "%H/%M/%S").time(),
    },
    UUID: {
        "serialize": lambda x: f"uuid:{x}",
        "deserialize": lambda s: UUID(s[5:]),
    },
}


class MyDialect(Dialect):
    serialization_strategy = serialization_strategy


@dataclass
class InnerDataClass(DataClassDictMixin):
    x: str


@dataclass
class DataClass(DataClassYAMLRocksMixin):
    x: str
    inner: InnerDataClass


def test_to_yaml():
    @dataclass
    class DataClass(DataClassYAMLRocksMixin):
        x: List[int]

    dumped = yamlrocks.dumps({"x": [1, 2, 3]})
    # to_yamlb returns the raw yamlrocks bytes; to_yaml decodes them to str
    assert DataClass([1, 2, 3]).to_yamlb() == dumped
    assert DataClass([1, 2, 3]).to_yaml() == dumped.decode()


def test_from_yaml():
    @dataclass
    class DataClass(DataClassYAMLRocksMixin):
        x: List[int]

    dumped = yamlrocks.dumps({"x": [1, 2, 3]})
    assert DataClass.from_yaml(dumped) == DataClass([1, 2, 3])
    # str input is accepted as well as bytes
    assert DataClass.from_yaml(dumped.decode()) == DataClass([1, 2, 3])


def test_yamlrocks_nested_roundtrip():
    instance = DataClass("a", InnerDataClass("b"))
    assert DataClass.from_yaml(instance.to_yaml()) == instance


def test_yamlrocks_native_types_passed_through():
    # datetime/date/time/UUID are serialized by yamlrocks itself, so the
    # encoded form matches what yamlrocks produces for the raw values.
    @dataclass
    class DataClass(DataClassYAMLRocksMixin):
        dt: datetime
        d: date
        t: time
        uid: UUID

    _dt = datetime(2022, 10, 12, 12, 54, 30)
    _d = date(2022, 10, 12)
    _t = time(12, 54, 30)
    _uid = uuid4()
    instance = DataClass(_dt, _d, _t, _uid)
    expected = yamlrocks.dumps({"dt": _dt, "d": _d, "t": _t, "uid": _uid})
    assert instance.to_yamlb() == expected
    assert DataClass.from_yaml(instance.to_yamlb()) == instance


def test_yamlrocks_with_serialization_strategy():
    @dataclass
    class DataClass(DataClassYAMLRocksMixin):
        datetime: List[datetime]
        date: List[date]
        time: List[time]
        uuid: List[UUID]

        class Config(BaseConfig):
            serialization_strategy = serialization_strategy

    _datetime = datetime(2022, 10, 12, 12, 54, 30)
    _date = date(2022, 10, 12)
    _time = time(12, 54, 30)
    _uuid = uuid4()
    dict_dumped = {
        "datetime": [_datetime.strftime("%Y/%m/%d/%H/%M/%S")],
        "date": [_date.toordinal()],
        "time": [_time.strftime("%H/%M/%S")],
        "uuid": [f"uuid:{_uuid}"],
    }
    instance = DataClass([_datetime], [_date], [_time], [_uuid])
    assert instance.to_dict() == dict_dumped
    assert instance.to_yamlb() == yamlrocks.dumps(dict_dumped)
    assert DataClass.from_yaml(yamlrocks.dumps(dict_dumped)) == instance


def test_yamlrocks_dumps_options_sort_keys():
    @dataclass
    class DataClass(DataClassYAMLRocksMixin):
        class Config(BaseConfig):
            yamlrocks_dumps_options = yamlrocks.OPT_SORT_KEYS

        b: int
        a: int

    assert DataClass(1, 2).to_yamlb() == yamlrocks.dumps(
        {"b": 1, "a": 2}, option=yamlrocks.OPT_SORT_KEYS
    )


def test_yamlrocks_loads_options_yaml_1_1():
    # Default parsing is YAML 1.2, where "yes" stays a string. The loads
    # option lets the mixin opt into YAML 1.1, where it becomes a bool.
    @dataclass
    class Default(DataClassYAMLRocksMixin):
        x: str

    @dataclass
    class Yaml11(DataClassYAMLRocksMixin):
        class Config(BaseConfig):
            yamlrocks_loads_options = yamlrocks.OPT_YAML_1_1

        x: str

    assert Default.from_yaml("x: yes").x == "yes"
    assert Yaml11.from_yaml("x: yes").x == "True"


def test_yamlrocks_options_survive_lazy_compilation():
    # Lazy compilation rebuilds the unpacker/packer on first use; the loads
    # and dumps options must be threaded through that rebuild.
    @dataclass
    class DataClass(DataClassYAMLRocksMixin):
        class Config(BaseConfig):
            lazy_compilation = True
            yamlrocks_loads_options = yamlrocks.OPT_YAML_1_1
            yamlrocks_dumps_options = yamlrocks.OPT_SORT_KEYS

        b: str
        a: str

    assert DataClass.from_yaml("b: yes\na: no") == DataClass("True", "False")
    assert DataClass("x", "y").to_yamlb() == yamlrocks.dumps(
        {"b": "x", "a": "y"}, option=yamlrocks.OPT_SORT_KEYS
    )


def test_yamlrocks_loads_and_dumps_options_together():
    @dataclass
    class DataClass(DataClassYAMLRocksMixin):
        class Config(BaseConfig):
            yamlrocks_loads_options = yamlrocks.OPT_YAML_1_1
            yamlrocks_dumps_options = yamlrocks.OPT_SORT_KEYS

        b: str
        a: str

    assert DataClass.from_yaml("b: yes\na: no") == DataClass("True", "False")
    assert DataClass("x", "y").to_yamlb() == yamlrocks.dumps(
        {"b": "x", "a": "y"}, option=yamlrocks.OPT_SORT_KEYS
    )
