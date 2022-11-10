from dataclasses import dataclass

import pytest
import typing_extensions

from mashumaro import DataClassDictMixin
from mashumaro.core.meta.helpers import is_not_required, is_required
from mashumaro.exceptions import InvalidFieldValue


class TypedDictCorrectNotRequired(typing_extensions.TypedDict):
    required: int
    not_required: typing_extensions.NotRequired[int]


class TypedDictCorrectRequired(typing_extensions.TypedDict, total=False):
    required: typing_extensions.Required[int]
    not_required: int


def test_is_required():
    assert is_required(typing_extensions.Required[int])
    assert not is_required(typing_extensions.Self)


def test_is_not_required():
    assert is_not_required(typing_extensions.NotRequired[int])
    assert not is_not_required(typing_extensions.Self)


def test_typed_dict_correct_not_required():
    @dataclass
    class MyClass(DataClassDictMixin):
        x: TypedDictCorrectNotRequired

    obj = MyClass({"required": 42})
    assert MyClass.from_dict({"x": {"required": 42}}) == obj
    assert obj.to_dict() == {"x": {"required": 42}}


def test_typed_dict_correct_required():
    @dataclass
    class MyClass(DataClassDictMixin):
        x: TypedDictCorrectRequired

    with pytest.raises(InvalidFieldValue) as exc_info:
        MyClass.from_dict({"x": {}})
    assert exc_info.type is InvalidFieldValue
    assert exc_info.value.holder_class is MyClass
    assert exc_info.value.field_type is TypedDictCorrectRequired
    assert exc_info.value.field_value == {}
    assert exc_info.value.field_name == "x"
