from dataclasses import dataclass
from datetime import date

import pytest

from mashumaro import DataClassDictMixin
from mashumaro.codecs import BasicDecoder, BasicEncoder
from mashumaro.exceptions import MissingField
from tests.entities_pep_695 import (
    Boxed,
    DataClassWithDirectRecursiveAlias,
    DataClassWithParameterizedAlias,
    DataClassWithRecursiveGenericAlias,
    DataClassWithWrappedRecursiveAlias,
    GenericListSerializable,
    GenericPassthroughSerializable,
)


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


# --- Integration tests for parameterized / recursive type aliases ---
# Uses types imported from another module to exercise cross-module name resolution.


def test_parameterized_generic_alias_as_type_arg():
    obj = DataClassWithParameterizedAlias(
        items=GenericListSerializable([1, 2, 3])
    )
    assert obj.to_dict() == {"items": [1, 2, 3]}
    assert (
        DataClassWithParameterizedAlias.from_dict({"items": [1, 2, 3]}) == obj
    )


def test_recursive_alias_direct():
    obj = DataClassWithDirectRecursiveAlias(items=[1, [2, [3]]])
    assert obj.to_dict() == {"items": [1, [2, [3]]]}
    assert (
        DataClassWithDirectRecursiveAlias.from_dict({"items": [1, [2, [3]]]})
        == obj
    )
    # Missing field must raise MissingField, not NameError
    with pytest.raises(MissingField):
        DataClassWithDirectRecursiveAlias.from_dict({})


def test_recursive_alias_wrapped():
    obj = DataClassWithWrappedRecursiveAlias(
        items=GenericPassthroughSerializable([1, [2, [3]]])
    )
    assert obj.to_dict() == {"items": [1, [2, [3]]]}
    assert (
        DataClassWithWrappedRecursiveAlias.from_dict({"items": [1, [2, [3]]]})
        == obj
    )


def test_recursive_generic_alias_with_serializable_type():
    """Recursive generic PEP 695 alias where the self-reference goes through
    a GenericSerializableType with a transformed type parameter.

    type Nested[T] = T | Boxed[Nested[tuple[str, T]]]
    """
    # Leaf value (the T branch of the union)
    obj1 = DataClassWithRecursiveGenericAlias(x=42)
    assert obj1.to_dict() == {"x": 42}
    assert DataClassWithRecursiveGenericAlias.from_dict({"x": 42}) == obj1

    # One level of nesting (the Boxed[Nested[tuple[str, T]]] branch)
    obj2 = DataClassWithRecursiveGenericAlias(x=Boxed(("hello", 7)))
    assert obj2.to_dict() == {"x": ("hello", 7)}
    assert (
        DataClassWithRecursiveGenericAlias.from_dict({"x": ("hello", 7)})
        == obj2
    )
