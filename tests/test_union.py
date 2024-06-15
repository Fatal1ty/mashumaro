from dataclasses import dataclass
from itertools import permutations
from typing import Any, Dict, List, Union

import pytest

from mashumaro import DataClassDictMixin
from mashumaro.codecs.basic import encode
from tests.utils import same_types


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


def test_union_encoding():
    for variants in permutations((int, float, str, bool)):
        for value in (1, 2.0, 3.1, "4", "5.0", True, False):
            encoded = encode(value, Union[variants])
            assert value == encoded
            assert same_types(value, encoded)


# TDDO: Convert this to a normal test
# def test_str_bool_union_warning():
#     with pytest.warns(UserWarning):
#
#         @dataclass
#         class _(DataClassDictMixin):
#             x: Union[str, bool]
