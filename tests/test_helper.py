from dataclasses import dataclass, field
from datetime import date, datetime

import pytest

from mashumaro import DataClassDictMixin, field_options
from mashumaro.helper import pass_through
from mashumaro.types import SerializationStrategy


def test_field_options_helper():
    assert field_options() == {
        "serialize": None,
        "deserialize": None,
        "serialization_strategy": None,
        "alias": None,
    }

    def serialize(x):
        return x  # pragma: no cover

    def deserialize(x):
        return x  # pragma: no cover

    class TestSerializationStrategy(SerializationStrategy):  # pragma: no cover
        def deserialize(self, value):
            return value

        def serialize(self, value):
            return value

    serialization_strategy = TestSerializationStrategy()
    alias = "alias"

    assert field_options(
        serialize=serialize,
        deserialize=deserialize,
        serialization_strategy=serialization_strategy,
        alias=alias,
    ) == {
        "serialize": serialize,
        "deserialize": deserialize,
        "serialization_strategy": serialization_strategy,
        "alias": alias,
    }


def test_pass_through():
    with pytest.raises(NotImplementedError):
        pass_through()
    assert pass_through.serialize(123) == 123
    assert pass_through.deserialize(123) == 123


def test_dataclass_with_pass_through():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(
            metadata=field_options(
                serialize=pass_through,
                deserialize=pass_through,
            )
        )
        y: date = field(
            metadata=field_options(serialization_strategy=pass_through)
        )

    x = datetime.now()
    y = x.date()
    instance = DataClass(x, y)
    assert instance.to_dict() == {"x": x, "y": y}
    assert instance.from_dict({"x": x, "y": y}) == instance
