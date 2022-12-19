import json
from dataclasses import dataclass
from datetime import datetime
from typing import List

import pytest

from mashumaro.exceptions import MissingField
from mashumaro.mixins.json import DataClassJSONMixin

from .entities import MyEnum


def test_to_json():
    @dataclass
    class DataClass(DataClassJSONMixin):
        x: List[int]

    dumped = json.dumps({"x": [1, 2, 3]})
    assert DataClass([1, 2, 3]).to_json() == dumped


def test_from_json():
    @dataclass
    class DataClass(DataClassJSONMixin):
        x: List[int]

    dumped = json.dumps({"x": [1, 2, 3]})
    assert DataClass.from_json(dumped) == DataClass([1, 2, 3])


def test_to_json_with_custom_encoder():
    @dataclass
    class DataClass(DataClassJSONMixin):
        x: List[int]
        x_count: int

    def encoder(d):
        dd = dict(d)
        dd.pop("x_count", None)
        return json.dumps(dd)

    instance = DataClass(x=[1, 2, 3], x_count=3)
    dumped = json.dumps({"x": [1, 2, 3]})
    assert instance.to_json(encoder=encoder) == dumped
    assert instance.to_json() != dumped


def test_from_json_with_custom_decoder():
    @dataclass
    class DataClass(DataClassJSONMixin):
        x: List[int]
        x_count: int

    def decoder(s):
        d = json.loads(s)
        d["x_count"] = len(d.get("x", []))
        return d

    instance = DataClass(x=[1, 2, 3], x_count=3)
    dumped = json.dumps({"x": [1, 2, 3]})
    assert DataClass.from_json(dumped, decoder=decoder) == instance
    with pytest.raises(MissingField):
        assert DataClass.from_json(dumped)


def test_json_enum():
    @dataclass
    class DataClass(DataClassJSONMixin):
        x: MyEnum

    dumped = '{"x": "letter a"}'
    instance = DataClass(MyEnum.a)

    assert instance.to_json() == dumped
    assert instance.to_json() == dumped
    assert DataClass.from_json(dumped) == instance


def test_json_bytes():
    @dataclass
    class DataClass(DataClassJSONMixin):
        x: bytes

    dumped = r'{"x": "MTIz\n"}'
    instance = DataClass(b"123")

    assert instance.to_json() == dumped
    assert DataClass.from_json(dumped) == instance


def test_json_datetime():
    dt = datetime(2018, 10, 29, 12, 46, 55, 308495)

    @dataclass
    class DataClass(DataClassJSONMixin):
        x: datetime

    dumped = json.dumps({"x": dt.isoformat()})
    instance = DataClass(x=dt)

    assert instance.to_json() == dumped
    assert DataClass.from_json(dumped) == instance
