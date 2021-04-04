from dataclasses import dataclass, field
from typing import Optional

import pytest

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig, TO_DICT_ADD_BY_ALIAS_FLAG
from mashumaro.exceptions import MissingField


@dataclass
class Aliased(DataClassDictMixin):
    a: int = field(metadata={"alias": "alias_a"})


@dataclass
class AliasedWithDefault(DataClassDictMixin):
    a: int = field(default=111, metadata={"alias": "alias_a"})


@dataclass
class AliasedWithDefaultNone(DataClassDictMixin):
    a: Optional[int] = field(default=None, metadata={"alias": "alias_a"})


@dataclass
class AliasedWithSerializeByAliasFlag(DataClassDictMixin):
    a: int = field(metadata={"alias": "alias_a"})

    class Config(BaseConfig):
        code_generation_options = [TO_DICT_ADD_BY_ALIAS_FLAG]


def test_alias():
    assert Aliased.from_dict({"alias_a": 123}) == Aliased(a=123)
    with pytest.raises(MissingField):
        assert Aliased.from_dict({"a": 123})


def test_alias_with_default():
    assert AliasedWithDefault.from_dict(
        {"alias_a": 123}
    ) == AliasedWithDefault(a=123)
    assert AliasedWithDefault.from_dict({}) == AliasedWithDefault(a=111)


def test_serialize_by_alias_code_generation_flag():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int = field(metadata={"alias": "alias"})

        class Config(BaseConfig):
            code_generation_options = [TO_DICT_ADD_BY_ALIAS_FLAG]

    instance = DataClass(x=123)
    assert instance.to_dict() == {"x": 123}
    assert instance.to_dict(by_alias=True) == {"alias": 123}


def test_serialize_by_alias_code_generation_flag_without_alias():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int

        class Config(BaseConfig):
            code_generation_options = [TO_DICT_ADD_BY_ALIAS_FLAG]

    instance = DataClass(x=123)
    assert instance.to_dict() == {"x": 123}
    assert instance.to_dict(by_alias=True) == {"x": 123}


def test_no_serialize_by_alias_code_generation_flag():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int = field(metadata={"alias": "alias"})

    instance = DataClass(x=123)
    assert instance.to_dict() == {"x": 123}
    with pytest.raises(TypeError):
        instance.to_dict(by_alias=True)


def test_serialize_by_alias_flag_for_inner_class_without_it():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Aliased = field(default=None, metadata={"alias": "alias_x"})

        class Config(BaseConfig):
            debug = True
            code_generation_options = [TO_DICT_ADD_BY_ALIAS_FLAG]

    instance = DataClass(Aliased(a=1))
    assert instance.to_dict() == {"x": {"a": 1}}
    assert instance.to_dict(by_alias=True) == {"alias_x": {"a": 1}}


def test_serialize_by_alias_flag_for_inner_class_with_it():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: AliasedWithSerializeByAliasFlag = field(
            default=None, metadata={"alias": "alias_x"}
        )

        class Config(BaseConfig):
            code_generation_options = [TO_DICT_ADD_BY_ALIAS_FLAG]

    instance = DataClass(AliasedWithSerializeByAliasFlag(a=1))
    assert instance.to_dict() == {"x": {"a": 1}}
    assert instance.to_dict(by_alias=True) == {"alias_x": {"alias_a": 1}}
