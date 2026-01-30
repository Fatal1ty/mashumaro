from dataclasses import dataclass
from datetime import date
from itertools import permutations
from typing import Any, Dict, List, Union

import pytest

from mashumaro import DataClassDictMixin, pass_through
from mashumaro.codecs.basic import encode
from mashumaro.config import BaseConfig
from mashumaro.dialect import Dialect
from tests.utils import same_types


@dataclass
class UnionTestCase:
    type: Any
    dumped: Any
    loaded: Any


@pytest.mark.parametrize(
    "test_case",
    [
        # int | str
        UnionTestCase(Union[int, str], 1, 1),
        UnionTestCase(Union[int, str], "1", "1"),
        UnionTestCase(Union[int, str], 1.0, 1),
        UnionTestCase(Union[int, str], 1.2, 1),
        UnionTestCase(Union[int, str], "a", "a"),
        UnionTestCase(Union[int, str], [1, 2], "[1, 2]"),
        # str | int
        UnionTestCase(Union[str, int], 1, 1),
        UnionTestCase(Union[str, int], "1", "1"),
        UnionTestCase(Union[str, int], 1.0, "1.0"),
        UnionTestCase(Union[str, int], 1.2, "1.2"),
        UnionTestCase(Union[str, int], "a", "a"),
        UnionTestCase(Union[str, int], [1, 2], "[1, 2]"),
        # str | date
        UnionTestCase(Union[str, date], "2024-11-12", "2024-11-12"),
        UnionTestCase(Union[str, date], "a", "a"),
        # date | str
        UnionTestCase(Union[date, str], "2024-11-12", date(2024, 11, 12)),
        UnionTestCase(Union[date, str], "a", "a"),
        # int | float
        UnionTestCase(Union[int, float], 1, 1),
        UnionTestCase(Union[int, float], 1.0, 1.0),
        UnionTestCase(Union[int, float], "1", 1),
        UnionTestCase(Union[int, float], "1.0", 1.0),
        # float | int
        UnionTestCase(Union[float, int], 1, 1),
        UnionTestCase(Union[float, int], 1.0, 1.0),
        UnionTestCase(Union[float, int], "1", 1.0),
        UnionTestCase(Union[float, int], "1.0", 1.0),
        # bool | int
        UnionTestCase(Union[bool, int], 1, 1),
        UnionTestCase(Union[bool, int], 1.0, True),
        UnionTestCase(Union[bool, int], True, True),
        UnionTestCase(Union[bool, int], "1", True),
        UnionTestCase(Union[bool, int], "1.2", True),
        UnionTestCase(Union[bool, int], [1, 2], True),
        UnionTestCase(Union[bool, int], "a", True),
        # int | bool
        UnionTestCase(Union[int, bool], 1, 1),
        UnionTestCase(Union[int, bool], 1.0, 1),
        UnionTestCase(Union[int, bool], True, True),
        UnionTestCase(Union[int, bool], "1", 1),
        UnionTestCase(Union[int, bool], "1.2", True),
        UnionTestCase(Union[int, bool], [1, 2], True),
        UnionTestCase(Union[int, bool], "a", True),
        # dict[int, int] | list[int]
        UnionTestCase(Union[Dict[int, int], List[int]], {1: 2}, {1: 2}),
        UnionTestCase(Union[Dict[int, int], List[int]], {"1": "2"}, {1: 2}),
        UnionTestCase(Union[Dict[int, int], List[int]], [1], [1]),
        UnionTestCase(Union[Dict[int, int], List[int]], ["1"], [1]),
        # str | list[str]
        UnionTestCase(Union[str, List[str]], ["a"], ["a"]),
        UnionTestCase(Union[str, List[str]], "abc", "abc"),
        UnionTestCase(Union[str, List[str]], 1, "1"),
        UnionTestCase(Union[str, List[str]], [1, 2], ["1", "2"]),
        # int | float | None
        UnionTestCase(Union[int, float, None], None, None),
        UnionTestCase(Union[int, float, None], 1, 1),
        UnionTestCase(Union[int, float, None], 1.2, 1.2),
        UnionTestCase(Union[int, float, None], "1", 1),
        UnionTestCase(Union[int, float, None], "1.2", 1.2),
        UnionTestCase(Union[int, float, None], "a", None),
        # None | int | float
        UnionTestCase(Union[None, int, float], None, None),
        UnionTestCase(Union[None, int, float], 1, 1),
        UnionTestCase(Union[None, int, float], 1.2, 1.2),
        UnionTestCase(Union[None, int, float], "1", None),
        UnionTestCase(Union[None, int, float], "1.2", None),
        UnionTestCase(Union[None, int, float], "a", None),
        # int | None | float
        UnionTestCase(Union[int, None, float], None, None),
        UnionTestCase(Union[int, None, float], 1, 1),
        UnionTestCase(Union[int, None, float], 1.2, 1.2),
        UnionTestCase(Union[int, None, float], "1", 1),
        UnionTestCase(Union[int, None, float], "1.2", None),
        UnionTestCase(Union[int, None, float], "a", None),
    ],
)
def test_union_deserialization(test_case):
    @dataclass
    class DataClass(DataClassDictMixin):
        x: test_case.type

    instance = DataClass(x=test_case.loaded)
    loaded = DataClass.from_dict({"x": test_case.dumped})
    assert loaded == instance
    assert same_types(loaded.x, instance.x)


@pytest.mark.parametrize(
    "test_case",
    [
        UnionTestCase(Union[int, str], 1, 1),
        UnionTestCase(Union[int, str], "1", "1"),
        UnionTestCase(Union[int, str], "a", "a"),
        UnionTestCase(Union[Dict[int, int], List[int]], {1: 2}, {1: 2}),
        UnionTestCase(Union[Dict[int, int], List[int]], [1], [1]),
        UnionTestCase(Union[str, List[str]], ["a"], ["a"]),
        UnionTestCase(Union[str, List[str]], "abc", "abc"),
    ],
)
def test_union_serialization(test_case):
    @dataclass
    class DataClass(DataClassDictMixin):
        x: test_case.type

    instance = DataClass(x=test_case.loaded)
    dumped = instance.to_dict()
    assert dumped == {"x": test_case.dumped}
    assert same_types(dumped["x"], test_case.dumped)


def test_union_encoding():
    for variants in permutations((int, float, str, bool)):
        for value in (1, 2.0, 3.1, "4", "5.0", True, False):
            encoded = encode(value, Union[variants])
            assert value == encoded
            assert same_types(value, encoded)


def test_union_no_copy_list_with_dataclass_items_or_passed_through_items():
    class NoCopyListDialect(Dialect):
        no_copy_collections = (list,)

    @dataclass
    class Item(DataClassDictMixin):
        value: int

    @dataclass
    class Container(DataClassDictMixin):
        items: Union[list[Item], list[str]]

        class Config(BaseConfig):
            dialect = NoCopyListDialect
            serialization_strategy = {str: {"serialize": lambda x: str(x)}}

    item1 = Item(1)
    item2 = Item(2)
    items = [item1, item2]
    container = Container(items=items)
    data = container.to_dict()
    assert data == {"items": [{"value": 1}, {"value": 2}]}
