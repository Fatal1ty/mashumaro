from __future__ import annotations

from dataclasses import dataclass

import pytest

from mashumaro import DataClassDictMixin
from mashumaro.config import ADD_DIALECT_SUPPORT, BaseConfig
from mashumaro.dialect import Dialect
from mashumaro.exceptions import UnresolvedTypeReferenceError

from .conftest import add_unpack_method


@dataclass
class A(DataClassDictMixin):
    x: B


@dataclass
class B(DataClassDictMixin):
    x: int


@dataclass
class Base(DataClassDictMixin):
    pass


@dataclass
class A1(Base):
    a: B1


@dataclass
class A2(Base):
    a: B2


@dataclass
class A3(Base):
    a: B1
    x: int

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]


@dataclass
class B1(Base):
    b: int


def test_postponed_annotation_evaluation():
    obj = A(x=B(x=1))
    assert obj.to_dict() == {"x": {"x": 1}}
    assert A.from_dict({"x": {"x": 1}}) == obj


def test_unresolved_type_with_allowed_postponed_annotation_evaluation():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: X

    with pytest.raises(UnresolvedTypeReferenceError):
        DataClass.from_dict({})

    with pytest.raises(UnresolvedTypeReferenceError):
        DataClass(x=1).to_dict()


def test_unresolved_type_with_disallowed_postponed_annotation_evaluation():
    with pytest.raises(UnresolvedTypeReferenceError):

        @dataclass
        class DataClass(DataClassDictMixin):
            x: X

            class Config(BaseConfig):
                allow_postponed_evaluation = False

    with add_unpack_method:
        with pytest.raises(UnresolvedTypeReferenceError):

            @dataclass
            class DataClass(DataClassDictMixin):
                x: X

                class Config(BaseConfig):
                    allow_postponed_evaluation = False


def test_postponed_annotation_evaluation_with_parent():
    obj = A1(B1(1))
    assert A1.from_dict({"a": {"b": 1}}) == obj
    assert obj.to_dict() == {"a": {"b": 1}}


def test_postponed_annotation_evaluation_with_parent_and_no_reference():
    with pytest.raises(UnresolvedTypeReferenceError):
        A2.from_dict({"a": {"b": 1}})
    with pytest.raises(UnresolvedTypeReferenceError):
        A2(None).to_dict()


def test_postponed_annotation_evaluation_with_parent_and_dialect():
    class MyDialect(Dialect):
        serialization_strategy = {
            int: {
                "serialize": lambda i: str(int(i * 1000)),
                "deserialize": lambda s: int(int(s) / 1000),
            }
        }

    obj = A3(B1(1), 2)
    assert A3.from_dict({"a": {"b": 1}, "x": 2}) == obj
    assert A3.from_dict({"a": {"b": 1}, "x": "2000"}, dialect=MyDialect) == obj
    assert obj.to_dict() == {"a": {"b": 1}, "x": 2}
    assert obj.to_dict(dialect=MyDialect) == {"a": {"b": 1}, "x": "2000"}
