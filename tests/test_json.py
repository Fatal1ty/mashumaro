import json
from dataclasses import dataclass
from typing import List

from mashumaro import DataClassJSONMixin


def test_to_json():
    @dataclass
    class DataClass(DataClassJSONMixin):
        x: List[int]
    dumped = json.dumps({'x': [1, 2, 3]})
    assert DataClass([1, 2, 3]).to_json() == dumped


def test_from_json():
    @dataclass
    class DataClass(DataClassJSONMixin):
        x: List[int]
    dumped = json.dumps({'x': [1, 2, 3]})
    assert DataClass.from_json(dumped) == DataClass([1, 2, 3])
