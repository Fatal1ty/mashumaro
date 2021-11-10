from dataclasses import dataclass, field
from typing import Optional, Union

import pytest

from mashumaro import DataClassDictMixin
from mashumaro.config import TO_DICT_ADD_OMIT_NONE_FLAG, BaseConfig
from mashumaro.meta.macros import PY_37_MIN
from mashumaro.types import SerializationStrategy

from .entities import (
    MyDataClassWithOptional,
    MyDataClassWithOptionalAndOmitNoneFlag,
    MyNamedTuple,
    MyNamedTupleWithDefaults,
    MyUntypedNamedTuple,
    TypedDictRequiredKeys,
)

if PY_37_MIN:
    from .entities import MyUntypedNamedTupleWithDefaults


def test_debug_true_option(mocker):
    mocked_print = mocker.patch("builtins.print")

    @dataclass
    class _(DataClassDictMixin):
        union: Union[int, str]
        typed_dict: TypedDictRequiredKeys
        named_tuple: MyNamedTupleWithDefaults

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


def test_named_tuple_as_dict():
    @dataclass
    class DataClass(DataClassDictMixin):
        mnp: MyNamedTuple
        mnpwd: MyNamedTupleWithDefaults
        munp: MyUntypedNamedTuple

        class Config(BaseConfig):
            namedtuple_as_dict = True

    obj = DataClass(
        mnp=MyNamedTuple(i=1, f=2.0),
        mnpwd=MyNamedTupleWithDefaults(i=1, f=2.0),
        munp=MyUntypedNamedTuple(i=1, f=2.0),
    )
    obj_dict = {
        "mnp": {"i": 1, "f": 2.0},
        "mnpwd": {"i": 1, "f": 2.0},
        "munp": {"i": 1, "f": 2.0},
    }
    assert obj.to_dict() == obj_dict
    assert DataClass.from_dict(obj_dict) == obj


@pytest.mark.skipif(not PY_37_MIN, reason="requires python>=3.7")
def test_untyped_named_tuple_with_defaults_as_dict():
    @dataclass
    class DataClass(DataClassDictMixin):
        munpwd: MyUntypedNamedTupleWithDefaults

        class Config(BaseConfig):
            namedtuple_as_dict = True

    obj = DataClass(munpwd=MyUntypedNamedTupleWithDefaults(i=1, f=2.0))
    assert obj.to_dict() == {"munpwd": {"i": 1, "f": 2.0}}
    assert DataClass.from_dict({"munpwd": {"i": 1, "f": 2.0}}) == obj


def test_named_tuple_as_dict_and_as_list_engine():
    @dataclass
    class DataClass(DataClassDictMixin):
        as_dict: MyNamedTuple
        as_list: MyNamedTuple = field(
            metadata={"serialize": "as_list", "deserialize": "as_list"}
        )

        class Config(BaseConfig):
            namedtuple_as_dict = True

    obj = DataClass(
        as_dict=MyNamedTuple(i=1, f=2.0),
        as_list=MyNamedTuple(i=1, f=2.0),
    )
    obj_dict = {
        "as_dict": {"i": 1, "f": 2.0},
        "as_list": [1, 2.0],
    }
    assert obj.to_dict() == obj_dict
    assert DataClass.from_dict(obj_dict) == obj
