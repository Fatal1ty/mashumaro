from datetime import datetime, timezone

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


def test_passing_kwargs_to_serialize():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(metadata=field_options(
            serialization_strategy=CustomDateSerdeStrategy()
        ))

        class Config(BaseConfig):
            code_generation_options = [PROPAGATE_KWARGS]

    target_dt = datetime(2020, 1, 1, tzinfo=timezone.utc)
    iso_dict = {"x": "2020-01-01T00:00:00+00:00"}
    unix_dict = {"x": 1577836800}

    assert DataClass(target_dt).to_dict() == iso_dict
    assert DataClass(target_dt).to_dict(unix=True) == unix_dict


def test_passing_kwargs_to_deserialize():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(metadata=field_options(
            serialization_strategy=CustomDateSerdeStrategy()
        ))

        class Config(BaseConfig):
            code_generation_options = [PROPAGATE_KWARGS]

    target_dt = datetime(2020, 1, 1, tzinfo=timezone.utc)
    iso_dict = {"x": "2020-01-01T00:00:00+00:00"}
    unix_dict = {"x": 1577836800}

    assert DataClass.from_dict(iso_dict).x == target_dt
    with pytest.raises(InvalidFieldValue):
        DataClass.from_dict(iso_dict, unix=True)

    assert DataClass.from_dict(unix_dict, unix=True).x == target_dt
    with pytest.raises(InvalidFieldValue):
        DataClass.from_dict(unix_dict)
