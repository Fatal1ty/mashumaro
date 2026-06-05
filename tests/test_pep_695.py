from dataclasses import dataclass
from datetime import date

import pytest

from mashumaro import DataClassDictMixin
from mashumaro.codecs import BasicDecoder, BasicEncoder
from mashumaro.config import TO_DICT_ADD_OMIT_NONE_FLAG, BaseConfig
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


def test_type_alias_type_nested_in_union():
    # https://github.com/Fatal1ty/mashumaro/issues/330
    type UniqueIdentifier = str
    type UniqueIdentifierList = list[UniqueIdentifier]
    type UniqueIdentifierOrList = UniqueIdentifier | UniqueIdentifierList

    @dataclass
    class MyClass(DataClassDictMixin):
        x: UniqueIdentifierOrList | None = None

    assert MyClass(x="a").to_dict() == {"x": "a"}
    assert MyClass(x=["a", "b"]).to_dict() == {"x": ["a", "b"]}
    assert MyClass().to_dict() == {"x": None}
    assert MyClass.from_dict({"x": "a"}) == MyClass(x="a")
    assert MyClass.from_dict({"x": ["a", "b"]}) == MyClass(x=["a", "b"])
    assert MyClass.from_dict({"x": None}) == MyClass()


@pytest.mark.parametrize("lazy", [False, True])
def test_type_alias_type_nested_in_union_with_omit_none_flag(lazy):
    type UniqueIdentifier = str
    type UniqueIdentifierList = list[UniqueIdentifier]
    type UniqueIdentifierOrList = UniqueIdentifier | UniqueIdentifierList

    @dataclass
    class MyClass(DataClassDictMixin):
        x: UniqueIdentifierOrList | None = None

        class Config(BaseConfig):
            code_generation_options = [TO_DICT_ADD_OMIT_NONE_FLAG]
            lazy_compilation = lazy

    assert MyClass(x="a").to_dict(omit_none=True) == {"x": "a"}
    assert MyClass(x=["a", "b"]).to_dict(omit_none=True) == {"x": ["a", "b"]}
    assert MyClass().to_dict(omit_none=True) == {}
    assert MyClass.from_dict({"x": ["a", "b"]}) == MyClass(x=["a", "b"])


def test_type_alias_type_nested_in_union_with_codecs():
    type UniqueIdentifier = str
    type UniqueIdentifierList = list[UniqueIdentifier]
    type UniqueIdentifierOrList = UniqueIdentifier | UniqueIdentifierList

    decoder = BasicDecoder(UniqueIdentifierOrList)
    encoder = BasicEncoder(UniqueIdentifierOrList)

    assert decoder.decode("a") == "a"
    assert decoder.decode(["a", "b"]) == ["a", "b"]
    assert encoder.encode("a") == "a"
    assert encoder.encode(["a", "b"]) == ["a", "b"]


def test_parameterized_type_alias_type_in_union():
    type Identity[T] = T
    type ListOf[T] = list[T]

    @dataclass
    class MyClass(DataClassDictMixin):
        x: date | ListOf[int]
        y: int | Identity[str]

    obj1 = MyClass(x=date(2024, 4, 15), y=42)
    assert obj1.to_dict() == {"x": "2024-04-15", "y": 42}
    assert MyClass.from_dict({"x": "2024-04-15", "y": 42}) == obj1

    obj2 = MyClass(x=[1, 2, 3], y="a")
    assert obj2.to_dict() == {"x": [1, 2, 3], "y": "a"}
    assert MyClass.from_dict({"x": [1, 2, 3], "y": "a"}) == obj2
