from dataclasses import dataclass
from typing import List

import yaml

from mashumaro.mixins.yaml import DataClassYAMLMixin


def test_to_yaml():
    @dataclass
    class DataClass(DataClassYAMLMixin):
        x: List[int]

    dumped = yaml.dump({"x": [1, 2, 3]})
    assert DataClass([1, 2, 3]).to_yaml() == dumped


def test_from_yaml():
    @dataclass
    class DataClass(DataClassYAMLMixin):
        x: List[int]

    dumped = yaml.dump({"x": [1, 2, 3]})
    assert DataClass.from_yaml(dumped) == DataClass([1, 2, 3])
