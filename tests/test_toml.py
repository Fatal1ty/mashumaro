from dataclasses import dataclass
from typing import List

import tomli_w

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

from mashumaro.mixins.toml import DataClassTOMLMixin


def test_to_toml():
    @dataclass
    class DataClass(DataClassTOMLMixin):
        x: List[int]

    dumped = tomli_w.dumps({"x": [1, 2, 3]})
    assert DataClass([1, 2, 3]).to_toml() == dumped


def test_from_toml():
    @dataclass
    class DataClass(DataClassTOMLMixin):
        x: List[int]

    dumped = tomli_w.dumps({"x": [1, 2, 3]})
    assert DataClass.from_toml(dumped) == DataClass([1, 2, 3])
