from dataclasses import dataclass
from typing import Optional, Union

import pytest

from mashumaro import DataClassDictMixin
from mashumaro.config import TO_DICT_ADD_OMIT_NONE_FLAG, BaseConfig
from mashumaro.types import SerializationStrategy

from .entities import (
    MyDataClassWithOptional,
    MyDataClassWithOptionalAndOmitNoneFlag,
    TypedDictRequiredKeys,
)


def test_debug_true_option(mocker):
    mocked_print = mocker.patch("builtins.print")

    @dataclass
    class _(DataClassDictMixin):
        union: Union[int, str]
        typed_dict: TypedDictRequiredKeys

        class Config(BaseConfig):
            debug = True

    mocked_print.assert_called()


def test_config_without_base_config_base(mocker):
    mocked_print = mocker.patch("builtins.print")

    @dataclass
    class _(DataClassDictMixin):
        x: Union[int, str]

        class Config:
            debug = True

    mocked_print.assert_called()


def test_debug_false_option(mocker):
    mocked_print = mocker.patch("builtins.print")

    @dataclass
    class _(DataClassDictMixin):
        x: Union[int, str]

        class Config(BaseConfig):
            debug = False

    mocked_print.assert_not_called()


def test_omit_none_code_generation_flag():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Optional[int] = None

        class Config(BaseConfig):
            code_generation_options = [TO_DICT_ADD_OMIT_NONE_FLAG]

    assert DataClass().to_dict() == {"x": None}
    assert DataClass().to_dict(omit_none=True) == {}


def test_no_omit_none_code_generation_flag():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Optional[int] = None

    assert DataClass().to_dict() == {"x": None}
    with pytest.raises(TypeError):
        DataClass().to_dict(omit_none=True)


def test_omit_none_flag_for_inner_class_without_it():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Optional[MyDataClassWithOptional] = None

        class Config(BaseConfig):
            code_generation_options = [TO_DICT_ADD_OMIT_NONE_FLAG]

    assert DataClass().to_dict() == {"x": None}
    assert DataClass().to_dict(omit_none=True) == {}

    empty_x = MyDataClassWithOptional()
    assert DataClass(empty_x).to_dict() == {"x": {"a": None, "b": None}}
    assert DataClass(empty_x).to_dict(omit_none=True) == {
        "x": {"a": None, "b": None}
    }


def test_omit_none_flag_for_inner_class_with_it():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Optional[MyDataClassWithOptionalAndOmitNoneFlag] = None

        class Config(BaseConfig):
            code_generation_options = [TO_DICT_ADD_OMIT_NONE_FLAG]

    assert DataClass().to_dict() == {"x": None}
    assert DataClass().to_dict(omit_none=True) == {}

    empty_x = MyDataClassWithOptionalAndOmitNoneFlag()
    assert DataClass(empty_x).to_dict() == {"x": {"a": None, "b": None}}
    assert DataClass(empty_x).to_dict(omit_none=True) == {"x": {}}


def test_passing_omit_none_into_union():
    @dataclass
    class DataClass(DataClassDictMixin):
        a: Optional[int] = None
        b: Optional[Union[int, MyDataClassWithOptionalAndOmitNoneFlag]] = None

        class Config(BaseConfig):
            code_generation_options = [TO_DICT_ADD_OMIT_NONE_FLAG]

    instance = DataClass(b=MyDataClassWithOptionalAndOmitNoneFlag(a=1))
    assert instance.to_dict(omit_none=True) == {"b": {"a": 1}}


def test_serialization_strategy():
    class TestSerializationStrategy(SerializationStrategy):
        def serialize(self, value):
            return [value]

        def deserialize(self, value):
            return value[0]

    @dataclass
    class DataClass(DataClassDictMixin):
        a: int
        b: str

        class Config(BaseConfig):
            serialization_strategy = {
                int: TestSerializationStrategy(),
                str: {
                    "serialize": lambda v: [v],
                    "deserialize": lambda v: v[0],
                },
            }

    instance = DataClass(a=123, b="abc")
    assert DataClass.from_dict({"a": [123], "b": ["abc"]}) == instance
    assert instance.to_dict() == {"a": [123], "b": ["abc"]}
