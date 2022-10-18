from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Dict, List
from uuid import UUID, uuid4

import orjson
import pytest

from mashumaro import DataClassDictMixin
from mashumaro.config import ADD_DIALECT_SUPPORT, BaseConfig
from mashumaro.dialect import Dialect
from mashumaro.mixins.orjson import DataClassORJSONMixin

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
class DataClass(DataClassORJSONMixin):
    x: str
    inner: InnerDataClass


def test_data_class_orjson_mixin():
    assert DataClassORJSONMixin.from_json("") is None
    assert DataClassORJSONMixin().to_jsonb() is None


def test_to_orjson():
    @dataclass
    class DataClass(DataClassORJSONMixin):
        x: List[int]

    dumped = orjson.dumps({"x": [1, 2, 3]})
    assert DataClass([1, 2, 3]).to_jsonb() == dumped
    assert DataClass([1, 2, 3]).to_json() == dumped.decode()


def test_from_orjson():
    @dataclass
    class DataClass(DataClassORJSONMixin):
        x: List[int]

    dumped = orjson.dumps({"x": [1, 2, 3]})
    assert DataClass.from_json(dumped) == DataClass([1, 2, 3])


def test_orjson_with_serialization_strategy():
    @dataclass
    class DataClass(DataClassORJSONMixin):
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
    _datetime_dumped = _datetime.strftime("%Y/%m/%d/%H/%M/%S")
    _date_dumped = _date.toordinal()
    _time_dumped = _time.strftime("%H/%M/%S")
    _uuid_dumped = f"uuid:{_uuid}"
    instance = DataClass([_datetime], [_date], [_time], [_uuid])
    dict_dumped = {
        "datetime": [_datetime_dumped],
        "date": [_date_dumped],
        "time": [_time_dumped],
        "uuid": [_uuid_dumped],
    }
    orjson_dumped = orjson.dumps(
        {
            "datetime": [_datetime_dumped],
            "date": [_date_dumped],
            "time": [_time_dumped],
            "uuid": [_uuid_dumped],
        }
    )
    assert DataClass.from_dict(dict_dumped) == instance
    assert DataClass.from_json(orjson_dumped) == instance
    assert instance.to_dict() == dict_dumped
    assert instance.to_jsonb() == orjson_dumped


def test_orjson_with_dialect():
    @dataclass
    class DataClass(DataClassORJSONMixin):
        datetime: List[datetime]
        date: List[date]
        time: List[time]
        uuid: List[UUID]

        class Config(BaseConfig):
            dialect = MyDialect

    _datetime = datetime(2022, 10, 12, 12, 54, 30)
    _date = date(2022, 10, 12)
    _time = time(12, 54, 30)
    _uuid = uuid4()
    _datetime_dumped = _datetime.strftime("%Y/%m/%d/%H/%M/%S")
    _date_dumped = _date.toordinal()
    _time_dumped = _time.strftime("%H/%M/%S")
    _uuid_dumped = f"uuid:{_uuid}"
    instance = DataClass([_datetime], [_date], [_time], [_uuid])
    dict_dumped = {
        "datetime": [_datetime_dumped],
        "date": [_date_dumped],
        "time": [_time_dumped],
        "uuid": [_uuid_dumped],
    }
    orjson_dumped = orjson.dumps(
        {
            "datetime": [_datetime_dumped],
            "date": [_date_dumped],
            "time": [_time_dumped],
            "uuid": [_uuid_dumped],
        }
    )
    assert DataClass.from_dict(dict_dumped) == instance
    assert DataClass.from_json(orjson_dumped) == instance
    assert instance.to_dict() == dict_dumped
    assert instance.to_jsonb() == orjson_dumped


def test_orjson_with_dialect_support():
    @dataclass
    class DataClass(DataClassORJSONMixin):
        datetime: List[datetime]
        date: List[date]
        time: List[time]
        uuid: List[UUID]

        class Config(BaseConfig):
            code_generation_options = [ADD_DIALECT_SUPPORT]

    _datetime = datetime(2022, 10, 12, 12, 54, 30)
    _date = date(2022, 10, 12)
    _time = time(12, 54, 30)
    _uuid = uuid4()
    _datetime_dumped = _datetime.strftime("%Y/%m/%d/%H/%M/%S")
    _date_dumped = _date.toordinal()
    _time_dumped = _time.strftime("%H/%M/%S")
    _uuid_dumped = f"uuid:{_uuid}"
    instance = DataClass([_datetime], [_date], [_time], [_uuid])
    dict_dumped = {
        "datetime": [_datetime.isoformat()],
        "date": [_date.isoformat()],
        "time": [_time.isoformat()],
        "uuid": [str(_uuid)],
    }
    dict_dumped_dialect = {
        "datetime": [_datetime_dumped],
        "date": [_date_dumped],
        "time": [_time_dumped],
        "uuid": [_uuid_dumped],
    }
    orjson_dumped = orjson.dumps(
        {
            "datetime": [_datetime],
            "date": [_date],
            "time": [_time],
            "uuid": [_uuid],
        }
    )
    orjson_dumped_dialect = orjson.dumps(
        {
            "datetime": [_datetime_dumped],
            "date": [_date_dumped],
            "time": [_time_dumped],
            "uuid": [_uuid_dumped],
        }
    )
    assert DataClass.from_dict(dict_dumped) == instance
    assert (
        DataClass.from_dict(dict_dumped_dialect, dialect=MyDialect) == instance
    )
    assert DataClass.from_json(orjson_dumped) == instance
    assert (
        DataClass.from_json(orjson_dumped_dialect, dialect=MyDialect)
        == instance
    )
    assert instance.to_dict() == dict_dumped
    assert instance.to_dict(dialect=MyDialect) == dict_dumped_dialect
    assert instance.to_jsonb() == orjson_dumped
    assert instance.to_jsonb(dialect=MyDialect) == orjson_dumped_dialect


def test_orjson_with_custom_encoder_and_decoder():
    def decoder(data) -> Dict[str, bytes]:
        def to_lower(d):
            result = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    result[k] = to_lower(v)
                else:
                    result[k] = v.lower()
            return result

        return to_lower(orjson.loads(data))

    def encoder(data: Dict[str, bytes], **_) -> bytes:
        def to_upper(d):
            result = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    result[k] = to_upper(v)
                else:
                    result[k] = v.upper()
            return result

        return orjson.dumps(to_upper(data))

    instance = DataClass("abc", InnerDataClass("def"))
    dumped = orjson.dumps({"x": "ABC", "inner": {"x": "DEF"}})
    assert instance.to_jsonb(encoder=encoder) == dumped
    assert DataClass.from_json(dumped, decoder=decoder) == instance


def test_to_orjson_with_non_str_keys():
    @dataclass
    class DataClass(DataClassORJSONMixin):
        x: Dict[int, int]

    instance = DataClass({1: 2})
    dumped = b'{"x":{"1":2}}'
    with pytest.raises(TypeError):
        instance.to_jsonb()
    assert instance.to_jsonb(orjson_options=orjson.OPT_NON_STR_KEYS) == dumped
    assert DataClass.from_json(dumped) == instance
