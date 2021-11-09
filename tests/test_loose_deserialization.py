from datetime import datetime, timezone

import pytest
from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin, field_options, MissingField
from mashumaro.config import BaseConfig, LOOSE_DESERIALIZE


def test_loose_deserialization():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: str = field(metadata=field_options(alias="FieldX"))

        class Config(BaseConfig):
            code_generation_options = [
                LOOSE_DESERIALIZE
            ]

    assert DataClass.from_dict({"FieldX": "Hello"}).x == "Hello"
    assert DataClass.from_dict({"x": "Hello"}).x == "Hello"


def test_strict_deserialization():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: str = field(metadata=field_options(alias="FieldX"))

    assert DataClass.from_dict({"FieldX": "Hello"}).x == "Hello"

    with pytest.raises(MissingField):
        DataClass.from_dict({"x": "Hello"}).x == "Hello"
