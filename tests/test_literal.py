from dataclasses import dataclass

import pytest
from typing_extensions import Literal

from mashumaro import DataClassDictMixin
from mashumaro.config import ADD_DIALECT_SUPPORT, BaseConfig
from mashumaro.dialect import Dialect
from mashumaro.exceptions import InvalidFieldValue
from mashumaro.helper import pass_through
from tests.entities import MyEnum


def test_literal_with_str():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Literal["1", "2", "3"]

    assert DataClass.from_dict({"x": "1"}) == DataClass("1")
    assert DataClass.from_dict({"x": "2"}) == DataClass("2")

    assert DataClass("1").to_dict() == {"x": "1"}
    assert DataClass("2").to_dict() == {"x": "2"}

    with pytest.raises(InvalidFieldValue):
        DataClass.from_dict({"x": 1})
    with pytest.raises(InvalidFieldValue):
        DataClass(1).to_dict()


def test_literal_with_int():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Literal[1, 2]

    assert DataClass.from_dict({"x": 1}) == DataClass(1)
    assert DataClass.from_dict({"x": 2}) == DataClass(2)

    assert DataClass(1).to_dict() == {"x": 1}
    assert DataClass(2).to_dict() == {"x": 2}

    with pytest.raises(InvalidFieldValue):
        DataClass.from_dict({"x": "1"})
    with pytest.raises(InvalidFieldValue):
        DataClass("1").to_dict()


def test_literal_with_bool():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Literal[True, False]

    assert DataClass.from_dict({"x": True}) == DataClass(True)
    assert DataClass.from_dict({"x": False}) == DataClass(False)

    with pytest.raises(InvalidFieldValue):
        DataClass.from_dict({"x": "a"})
    with pytest.raises(InvalidFieldValue):
        DataClass("a").to_dict()


def test_literal_with_none():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Literal[None]

    assert DataClass.from_dict({"x": None}) == DataClass(None)
    assert DataClass(None).to_dict() == {"x": None}
    with pytest.raises(InvalidFieldValue):
        DataClass.from_dict({"x": "1"})
    with pytest.raises(InvalidFieldValue):
        DataClass("1").to_dict()


def test_literal_with_bytes():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Literal[b"\x00"]

    assert DataClass.from_dict({"x": "AA==\n"}) == DataClass(b"\x00")
    assert DataClass(b"\x00").to_dict() == {"x": "AA==\n"}
    with pytest.raises(InvalidFieldValue):
        DataClass.from_dict({"x": "\x00"})
    with pytest.raises(InvalidFieldValue):
        DataClass("AA==\n").to_dict()


def test_literal_with_bytes_overridden():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Literal[b"\x00"]

        class Config(BaseConfig):
            serialization_strategy = {bytes: pass_through}

    assert DataClass.from_dict({"x": b"\x00"}) == DataClass(b"\x00")
    assert DataClass(b"\x00").to_dict() == {"x": b"\x00"}
    with pytest.raises(InvalidFieldValue):
        DataClass.from_dict({"x": "AA==\n"})


def test_literal_with_enum():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Literal[MyEnum.a]

    assert DataClass.from_dict({"x": "letter a"}) == DataClass(MyEnum.a)
    with pytest.raises(InvalidFieldValue):
        DataClass.from_dict({"x": "letter b"})
    with pytest.raises(InvalidFieldValue):
        DataClass(MyEnum.b).to_dict()


def test_literal_with_dialect():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Literal[b"\x00"]

        class Config(BaseConfig):
            code_generation_options = [ADD_DIALECT_SUPPORT]

    class MyDialect(Dialect):
        serialization_strategy = {bytes: pass_through}

    instance = DataClass(b"\x00")
    assert DataClass.from_dict({"x": b"\x00"}, dialect=MyDialect) == instance
    assert instance.to_dict(dialect=MyDialect) == {"x": b"\x00"}
    with pytest.raises(InvalidFieldValue):
        DataClass.from_dict({"x": "AA==\n"}, dialect=MyDialect)
