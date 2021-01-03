from dataclasses import dataclass, field
from datetime import datetime, timezone, date, time
from mashumaro import DataClassDictMixin


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
