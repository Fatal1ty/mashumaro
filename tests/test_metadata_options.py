from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from pathlib import Path

import ciso8601
import pytest

from mashumaro import DataClassDictMixin
from mashumaro.exceptions import UnserializableField

from .entities import MutableString, ThirdPartyType


def test_ciso8601_datetime_parser():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(metadata={"deserialize": "ciso8601"})

    should_be = DataClass(x=datetime(2021, 1, 2, 3, 4, 5, tzinfo=timezone.utc))
    instance = DataClass.from_dict({"x": "2021-01-02T03:04:05Z"})
    assert instance == should_be


def test_ciso8601_date_parser():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: date = field(metadata={"deserialize": "ciso8601"})

    should_be = DataClass(x=date(2021, 1, 2))
    instance = DataClass.from_dict({"x": "2021-01-02T03:04:05Z"})
    assert instance == should_be


def test_ciso8601_time_parser():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: time = field(metadata={"deserialize": "ciso8601"})

    should_be = DataClass(x=time(3, 4, 5))
    instance = DataClass.from_dict({"x": "2021-01-02T03:04:05Z"})
    assert instance == should_be


def test_pendulum_datetime_parser():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(metadata={"deserialize": "pendulum"})

    should_be = DataClass(x=datetime(2008, 12, 29, 7, tzinfo=timezone.utc))
    instance = DataClass.from_dict({"x": "2009-W01 0700"})
    assert instance == should_be


def test_pendulum_date_parser():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: date = field(metadata={"deserialize": "pendulum"})

    should_be = DataClass(x=date(2008, 12, 29))
    instance = DataClass.from_dict({"x": "2009-W01"})
    assert instance == should_be


def test_pendulum_time_parser():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: time = field(metadata={"deserialize": "pendulum"})

    should_be = DataClass(x=time(3, 4, 5))
    instance = DataClass.from_dict({"x": "2009-W01 030405"})
    assert instance == should_be


def test_unsupported_datetime_parser_engine():
    with pytest.raises(UnserializableField):

        @dataclass
        class DataClass(DataClassDictMixin):
            x: datetime = field(metadata={"deserialize": "unsupported"})


def test_global_function_datetime_parser():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(
            metadata={"deserialize": ciso8601.parse_datetime_as_naive}
        )

    should_be = DataClass(x=datetime(2021, 1, 2, 3, 4, 5))
    instance = DataClass.from_dict({"x": "2021-01-02T03:04:05+03:00"})
    assert instance == should_be


def test_local_function_datetime_parser():
    def parse_dt(s):
        return ciso8601.parse_datetime_as_naive(s)

    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(metadata={"deserialize": parse_dt})

    should_be = DataClass(x=datetime(2021, 1, 2, 3, 4, 5))
    instance = DataClass.from_dict({"x": "2021-01-02T03:04:05+03:00"})
    assert instance == should_be


def test_class_method_datetime_parser():
    class DateTimeParser:
        @classmethod
        def parse_dt(cls, s: str) -> datetime:
            return datetime.fromisoformat(s)

    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(metadata={"deserialize": DateTimeParser.parse_dt})

    should_be = DataClass(x=datetime(2021, 1, 2, 3, 4, 5))
    instance = DataClass.from_dict({"x": "2021-01-02T03:04:05"})
    assert instance == should_be


def test_class_instance_method_datetime_parser():
    class DateTimeParser:
        def __call__(self, s: str) -> datetime:
            return datetime.fromisoformat(s)

    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(metadata={"deserialize": DateTimeParser()})

    should_be = DataClass(x=datetime(2021, 1, 2, 3, 4, 5))
    instance = DataClass.from_dict({"x": "2021-01-02T03:04:05"})
    assert instance == should_be


def test_callable_class_instance_datetime_parser():
    class CallableDateTimeParser:
        def __call__(self, s):
            return ciso8601.parse_datetime(s)

    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(metadata={"deserialize": CallableDateTimeParser()})

    should_be = DataClass(x=datetime(2021, 1, 2, 3, 4, 5, tzinfo=timezone.utc))
    instance = DataClass.from_dict({"x": "2021-01-02T03:04:05Z"})
    assert instance == should_be


def test_lambda_datetime_parser():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(
            metadata={"deserialize": lambda s: ciso8601.parse_datetime(s)}
        )

    should_be = DataClass(x=datetime(2021, 1, 2, 3, 4, 5, tzinfo=timezone.utc))
    instance = DataClass.from_dict({"x": "2021-01-02T03:04:05Z"})
    assert instance == should_be


def test_derived_dataclass_metadata_deserialize_option():
    @dataclass
    class A:
        x: datetime = field(metadata={"deserialize": ciso8601.parse_datetime})

    @dataclass
    class B(A, DataClassDictMixin):
        y: datetime = field(metadata={"deserialize": ciso8601.parse_datetime})

    should_be = B(
        x=datetime(2021, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
        y=datetime(2021, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
    )
    instance = B.from_dict(
        {"x": "2021-01-02T03:04:05Z", "y": "2021-01-02T03:04:05Z"}
    )
    assert instance == should_be


def test_bytearray_overridden():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: bytearray = field(
            metadata={"deserialize": lambda s: s.upper().encode()}
        )

    should_be = DataClass(x=bytearray(b"ABC"))
    instance = DataClass.from_dict({"x": "abc"})
    assert instance == should_be


def test_path_like_overridden():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Path = field(
            metadata={"deserialize": lambda s: Path(str(s).upper())}
        )

    should_be = DataClass(x=Path("/ABC"))
    instance = DataClass.from_dict({"x": "/abc"})
    assert instance == should_be


def test_datetime_serialize_option():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(
            metadata={"serialize": lambda v: v.strftime("%Y-%m-%d %H:%M:%S")}
        )

    should_be = {"x": "2021-01-02 03:04:05"}
    instance = DataClass(x=datetime(2021, 1, 2, 3, 4, 5, tzinfo=timezone.utc))
    assert instance.to_dict() == should_be


def test_third_party_type_overridden():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: ThirdPartyType = field(
            metadata={
                "deserialize": lambda v: ThirdPartyType(v),
                "serialize": lambda v: v.value,
            }
        )

    should_be = DataClass(x=ThirdPartyType(123))
    instance = DataClass.from_dict({"x": 123})
    assert instance == should_be
    assert instance.to_dict() == {"x": 123}


def test_serializable_type_overridden():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MutableString = field(
            metadata={
                "deserialize": lambda s: MutableString(s.upper()),
                "serialize": lambda v: str(v).lower(),
            }
        )

    should_be = DataClass(x=MutableString("ABC"))
    instance = DataClass.from_dict({"x": "abc"})
    assert instance == should_be
    assert instance.to_dict() == {"x": "abc"}
