from dataclasses import dataclass
from typing import Any, ClassVar, Dict

import pytest

from mashumaro import DataClassDictMixin


def test_bad_pre_deserialize_hook():
    with pytest.raises(Exception):

        class DataClass(DataClassDictMixin):
            x: int

            def __pre_deserialize__(self, d: Dict[Any, Any]) -> Dict[Any, Any]:
                pass  # pragma no cover

        obj = DataClass.from_dict({"x": 2})  # noqa: F841


def test_bad_post_deserialize_hook():
    with pytest.raises(Exception):

        class DataClass(DataClassDictMixin):
            x: int

            def __post_deserialize__(self, obj: "DataClass") -> "DataClass":
                pass  # pragma no cover

        obj = DataClass.from_dict({"x": 2})  # noqa: F841


def test_pre_deserialize_hook():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int

        @classmethod
        def __pre_deserialize__(cls, d: Dict[Any, Any]) -> Dict[Any, Any]:
            return {k.lower(): v for k, v in d.items()}

    assert DataClass.from_dict({"X": 123}) == DataClass(x=123)


def test_post_deserialize_hook():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int

        @classmethod
        def __post_deserialize__(cls, obj: "DataClass") -> "DataClass":
            obj.x = 456
            return obj

    assert DataClass.from_dict({"x": 123}) == DataClass(x=456)


def test_pre_serialize_hook():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int
        counter: ClassVar[int] = 0

        def __pre_serialize__(self) -> "DataClass":
            self.counter += 1
            return self

    instance = DataClass(x=123)
    assert instance.to_dict() == {"x": 123}
    assert instance.counter == 1


def test_post_serialize_hook():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: int
        counter: ClassVar[int] = 0

        def __post_serialize__(self, d: Dict[Any, Any]) -> Dict[Any, Any]:
            return {k.upper(): v for k, v in d.items()}

    instance = DataClass(x=123)
    assert instance.to_dict() == {"X": 123}


def test_superclass_post_serialize_hook():
    @dataclass
    class MyDataClassMixin(DataClassDictMixin):
        def __post_serialize__(self, d: Dict[Any, Any]) -> Dict[Any, Any]:
            return {k.upper(): v for k, v in d.items()}

    @dataclass
    class DataClassA(MyDataClassMixin):
        x: int
        counter: ClassVar[int] = 0

    instance = DataClassA(x=123)
    assert instance.to_dict() == {"X": 123}
