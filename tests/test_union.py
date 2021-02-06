from dataclasses import dataclass
from typing import Any, Dict, List, Union

import pytest

from mashumaro import DataClassDictMixin


@dataclass
class UnionTestCase:
    type: Any
    dumped: Any
    loaded: Any


@pytest.mark.parametrize(
    "test_case",
    [
        UnionTestCase(Union[int, str], 1, 1),
        UnionTestCase(Union[int, str], "a", "a"),
        UnionTestCase(Union[Dict[int, int], List[int]], {1: 2}, {1: 2}),
        UnionTestCase(Union[Dict[int, int], List[int]], [1], [1]),
        UnionTestCase(Union[str, List[str]], ["a"], ["a"]),
        UnionTestCase(Union[str, List[str]], "abc", "abc"),
    ],
)
def test_union(test_case):
    @dataclass
    class DataClass(DataClassDictMixin):
        x: test_case.type

    instance = DataClass(x=test_case.loaded)
    assert DataClass.from_dict({"x": test_case.dumped}) == instance
    assert instance.to_dict() == {"x": test_case.dumped}
