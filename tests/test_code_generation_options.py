from dataclasses import dataclass
from typing import Optional

from mashumaro import DataClassDictMixin
from mashumaro.config import (
    TO_DICT_ADD_BY_ALIAS_FLAG,
    TO_DICT_ADD_OMIT_NONE_FLAG,
    BaseConfig,
)


@dataclass
class A(DataClassDictMixin):
    x: Optional[int] = None

    class Config(BaseConfig):
        aliases = {"x": "x_alias"}
        code_generation_options = [
            TO_DICT_ADD_OMIT_NONE_FLAG,
            TO_DICT_ADD_BY_ALIAS_FLAG,
        ]


@dataclass
class B(DataClassDictMixin):
    a: Optional[A] = None

    class Config(BaseConfig):
        aliases = {"a": "a_alias"}
        code_generation_options = [
            TO_DICT_ADD_OMIT_NONE_FLAG,
            TO_DICT_ADD_BY_ALIAS_FLAG,
        ]


def test_passing_flags_if_parent_has_them():
    @dataclass
    class WithFlags(DataClassDictMixin):
        b: B

        class Config(BaseConfig):
            code_generation_options = [
                TO_DICT_ADD_OMIT_NONE_FLAG,
                TO_DICT_ADD_BY_ALIAS_FLAG,
            ]

    assert WithFlags.from_dict({"b": {"a": {"x": None}}}) == WithFlags(
        b=B(a=None)
    )
    obj = WithFlags.from_dict({"b": {"a_alias": {"x": None}}})
    assert obj == WithFlags(b=B(a=A(x=None)))
    assert obj.to_dict() == {"b": {"a": {"x": None}}}
    assert obj.to_dict(by_alias=True) == {"b": {"a_alias": {"x_alias": None}}}
    assert obj.to_dict(by_alias=True, omit_none=True) == {"b": {"a_alias": {}}}


def test_passing_flags_if_parent_does_not_have_them():
    @dataclass
    class WithoutFlags(DataClassDictMixin):
        b: B

    assert WithoutFlags.from_dict({"b": {"a": {"x": None}}}) == WithoutFlags(
        b=B(a=None)
    )
    obj = WithoutFlags.from_dict({"b": {"a_alias": {"x": None}}})
    assert obj == WithoutFlags(b=B(a=A(x=None)))
    assert obj.to_dict() == {"b": {"a": {"x": None}}}
