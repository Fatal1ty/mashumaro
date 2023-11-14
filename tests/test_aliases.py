from dataclasses import dataclass, field
from typing import Optional

import pytest

from mashumaro import DataClassDictMixin
from mashumaro.config import (
    TO_DICT_ADD_BY_ALIAS_FLAG,
    TO_DICT_ADD_OMIT_NONE_FLAG,
    BaseConfig,
)
from mashumaro.exceptions import MissingField


@dataclass
class Aliased(DataClassDictMixin):
    a: int = field(metadata={"alias": "alias_a"})


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
    @dataclass
    class DataClass(DataClassDictMixin):
        a: int = field(default=111, metadata={"alias": "alias_a"})

    assert DataClass.from_dict({"alias_a": 123}) == DataClass(a=123)
    assert DataClass.from_dict({}) == DataClass(a=111)


def test_alias_with_omit_none():
    @dataclass
    class DataClass(DataClassDictMixin):
        a: Optional[int] = field(default=None, metadata={"alias": "alias_a"})

        class Config(BaseConfig):
            code_generation_options = [
                TO_DICT_ADD_BY_ALIAS_FLAG,
                TO_DICT_ADD_OMIT_NONE_FLAG,
            ]

    instance = DataClass()
    assert instance.to_dict(omit_none=True) == {}
    assert instance.to_dict(by_alias=True) == {"alias_a": None}
    assert instance.to_dict(omit_none=True, by_alias=True) == {}
    instance = DataClass(a=123)
    assert instance.to_dict(omit_none=True) == {"a": 123}
    assert instance.to_dict(by_alias=True) == {"alias_a": 123}
    assert instance.to_dict(omit_none=True, by_alias=True) == {"alias_a": 123}


def test_serialize_by_alias_config_option():
    @dataclass
    class DataClass(DataClassDictMixin):
        a: int = field(metadata={"alias": "alias_a"})

        class Config(BaseConfig):
            serialize_by_alias = True

    assert DataClass(123).to_dict() == {"alias_a": 123}


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


def test_aliases_in_config():
    @dataclass
    class DataClass(DataClassDictMixin):
        a: int = 111

        class Config(BaseConfig):
            aliases = {"a": "alias_a"}
            serialize_by_alias = True

    assert DataClass.from_dict({"alias_a": 123}) == DataClass(a=123)
    assert DataClass.from_dict({}) == DataClass(a=111)
    assert DataClass(a=123).to_dict() == {"alias_a": 123}


def test_by_alias_with_serialize_by_alias():
    @dataclass
    class DataClass(DataClassDictMixin):
        a: int = field(metadata={"alias": "alias_a"})

        class Config(BaseConfig):
            serialize_by_alias = True
            code_generation_options = [TO_DICT_ADD_BY_ALIAS_FLAG]

    instance = DataClass(a=123)
    assert DataClass.from_dict({"alias_a": 123}) == instance
    assert instance.to_dict() == {"alias_a": 123}
    assert instance.to_dict(by_alias=False) == {"a": 123}


def test_no_serialize_by_alias_with_serialize_by_alias_and_optional():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Optional[int] = field(metadata={"alias": "alias"})

        class Config(BaseConfig):
            serialize_by_alias = True

    assert DataClass(x=123).to_dict() == {"alias": 123}
    assert DataClass(x=None).to_dict() == {"alias": None}


def test_by_field_with_loose_deserialize():
    @dataclass
    class DataClass(DataClassDictMixin):
        a: int = field(metadata={"alias": "alias_a"})
        b: Optional[int] = field(metadata={"alias": "alias_b"})
        c: Optional[str] = field(metadata={"alias": "alias_c"})
        d: int = field(metadata={"alias": "alias_d"}, default=4)
        e: Optional[int] = field(metadata={"alias": "alias_e"}, default=5)
        f: Optional[str] = field(metadata={"alias": "alias_f"}, default="6")

        class Config(BaseConfig):
            serialize_by_alias = True
            code_generation_options = [TO_DICT_ADD_BY_ALIAS_FLAG]
            allow_deserialization_not_by_alias = True

    instance = DataClass(a=1, b=2, c="3")
    assert (
        DataClass.from_dict(
            {
                "a": 1,
                "alias_b": 2,
                "c": "3",
                "alias_d": 4,
                "e": 5,
                "alias_f": "6",
            }
        )
        == instance
    )
    assert instance.to_dict() == {
        "alias_a": 1,
        "alias_b": 2,
        "alias_c": "3",
        "alias_d": 4,
        "alias_e": 5,
        "alias_f": "6",
    }
    assert instance.to_dict(by_alias=False) == {
        "a": 1,
        "b": 2,
        "c": "3",
        "d": 4,
        "e": 5,
        "f": "6",
    }
