from dataclasses import dataclass

from mashumaro import DataClassDictMixin
from tests.entities import GenericSerializableList


def test_generic_serializable_list_int():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: GenericSerializableList[int]

    obj = DataClass(x=GenericSerializableList([1, 2, 3]))
    assert DataClass.from_dict({"x": [3, 4, 5]}) == obj
    assert obj.to_dict() == {"x": [3, 4, 5]}


def test_generic_serializable_list_str():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: GenericSerializableList[str]

    obj = DataClass(x=GenericSerializableList(["a", "b", "c"]))
    assert DataClass.from_dict({"x": ["_a", "_b", "_c"]}) == obj
    assert obj.to_dict() == {"x": ["_a", "_b", "_c"]}
