from datetime import datetime, timezone
from typing import List

import pytest
from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin, field_options
from mashumaro.config import BaseConfig, PROPAGATE_KWARGS
from mashumaro.exceptions import InvalidFieldValue
from mashumaro.types import SerializationStrategy


class CustomDateSerdeStrategy(SerializationStrategy):

    def serialize(self, value: datetime, unix: bool = False):
        if unix:
            return int(value.timestamp())
        return value.isoformat()

    def deserialize(self, value, unix: bool = False):
        if unix:
            if not isinstance(value, int):
                raise TypeError("Unexpected Value")
            return datetime.utcfromtimestamp(value)\
                .replace(tzinfo=timezone.utc)
        else:
            if not isinstance(value, str):
                raise TypeError("Unexpected Value")
            return datetime.fromisoformat(value)

@dataclass
class SubDataClass(DataClassDictMixin):
    x2: datetime = field(metadata=field_options(
        serialization_strategy=CustomDateSerdeStrategy()
    ))

    class Config(BaseConfig):
        code_generation_options = [PROPAGATE_KWARGS]

@dataclass
class DataClass(DataClassDictMixin):
    sdc: List[SubDataClass]
    x: datetime = field(metadata=field_options(
        serialization_strategy=CustomDateSerdeStrategy()
    ))

    class Config(BaseConfig):
        code_generation_options = [PROPAGATE_KWARGS]


def test_passing_kwargs_to_serialize():
    target_dt = datetime(2020, 1, 1, tzinfo=timezone.utc)
    iso_dict = {
        "x": "2020-01-01T00:00:00+00:00",
        "sdc": [{
            "x2": "2020-01-01T00:00:00+00:00"
        }]
    }
    unix_dict = {
        "x": 1577836800,
        "sdc": [{
            "x2": 1577836800
        }]
    }

    dc = DataClass(sdc=[SubDataClass(x2=target_dt)], x=target_dt)
    assert dc.to_dict() == iso_dict
    assert dc.to_dict(unix=True) == unix_dict


def test_passing_kwargs_to_deserialize():

    target_dt = datetime(2020, 1, 1, tzinfo=timezone.utc)
    iso_dict = {
        "x": "2020-01-01T00:00:00+00:00",
        "sdc": [{
            "x2": "2020-01-01T00:00:00+00:00"
        }]
    }
    unix_dict = {
        "x": 1577836800,
        "sdc": [{
            "x2": 1577836800
        }]
    }

    assert DataClass.from_dict(iso_dict).x == target_dt
    assert DataClass.from_dict(iso_dict).sdc[0].x2 == target_dt
    with pytest.raises(InvalidFieldValue):
        DataClass.from_dict(iso_dict, unix=True)

    assert DataClass.from_dict(unix_dict, unix=True).x == target_dt
    assert DataClass.from_dict(unix_dict, unix=True).sdc[0].x2 == target_dt
    with pytest.raises(InvalidFieldValue):
        DataClass.from_dict(unix_dict)
