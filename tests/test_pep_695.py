from dataclasses import dataclass
from datetime import date

import pytest

from mashumaro import DataClassDictMixin
from mashumaro.codecs import BasicDecoder, BasicEncoder


def test_type_alias_type_with_dataclass_dict_mixin():
    type MyDate = date

    @dataclass
    class MyClass(DataClassDictMixin):
        x: MyDate

    obj = MyClass(date(2024, 4, 15))
    assert MyClass.from_dict({"x": "2024-04-15"}) == obj
    assert obj.to_dict() == {"x": "2024-04-15"}


def test_type_alias_type_with_codecs():
    type MyDate = date
    decoder = BasicDecoder(MyDate)
    encoder = BasicEncoder(MyDate)

    obj = date(2024, 4, 15)
    assert decoder.decode("2024-04-15") == obj
    assert encoder.encode(obj) == "2024-04-15"


@pytest.mark.parametrize("deferred_ann", [False, True])
def test_pep695_generic_serialization_strategy(deferred_ann):
    if deferred_ann:
        from tests.entities_pep_695_deferred_ann import (
            DataClassWithPEP695SerializationStrategy,
            Leaf,
        )
    else:
        from tests.entities_pep_695 import (
            DataClassWithPEP695SerializationStrategy,
            Leaf,
        )

    obj = DataClassWithPEP695SerializationStrategy(
        set([Leaf(v=1), Leaf(v=2), Leaf(v=3), Leaf(v=4), Leaf(v=5)])
    )
    assert obj.to_dict() == {
        "x": [{"v": 1}, {"v": 2}, {"v": 3}, {"v": 4}, {"v": 5}]
    }
    assert (
        DataClassWithPEP695SerializationStrategy.from_dict(
            {"x": [{"v": 1}, {"v": 2}, {"v": 3}, {"v": 4}, {"v": 5}]}
        )
        == obj
    )


@pytest.mark.parametrize("deferred_ann", [False, True])
def test_pep695_generic_serializable_type(deferred_ann):
    if deferred_ann:
        from tests.entities_pep_695_deferred_ann import (
            DataClassWithPEP695SerializableType,
            PEP695GenericSerializableList,
        )
    else:
        from tests.entities_pep_695 import (
            DataClassWithPEP695SerializableType,
            PEP695GenericSerializableList,
        )

    obj = DataClassWithPEP695SerializableType(
        PEP695GenericSerializableList(["a", "b", "c"])
    )
    assert obj.to_dict() == {"x": ["a", "b", "c"]}
    assert (
        DataClassWithPEP695SerializableType.from_dict({"x": ["a", "b", "c"]})
        == obj
    )
