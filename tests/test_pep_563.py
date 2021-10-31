from __future__ import annotations

import pytest
from dataclasses import dataclass

from mashumaro import DataClassDictMixin
from mashumaro.exceptions import UnresolvedTypeReferenceError
from mashumaro.config import BaseConfig


@dataclass
class A(DataClassDictMixin):
    x: B


@dataclass
class B(DataClassDictMixin):
    x: int


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
