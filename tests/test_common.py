from dataclasses import dataclass

import pytest

from mashumaro import (
    DataClassDictMixin,
    DataClassJSONMixin,
    DataClassMessagePackMixin,
    DataClassYAMLMixin,
)


def test_slots():
    @dataclass
    class RegularDataClass:
        __slots__ = ("number",)
        number: int

    @dataclass
    class DictDataClass(DataClassDictMixin):
        __slots__ = ("number",)
        number: int

    @dataclass
    class JSONDataClass(DataClassJSONMixin):
        __slots__ = ("number",)
        number: int

    @dataclass
    class MessagePackDataClass(DataClassMessagePackMixin):
        __slots__ = ("number",)
        number: int

    @dataclass
    class YAMLDataClass(DataClassYAMLMixin):
        __slots__ = ("number",)
        number: int

    for cls in (
        RegularDataClass,
        DictDataClass,
        JSONDataClass,
        MessagePackDataClass,
        YAMLDataClass,
    ):
        instance = cls(1)
        with pytest.raises(AttributeError) as e:
            instance.new_attribute = 2
        assert (
            str(e.value)
            == f"'{cls.__name__}' object has no attribute 'new_attribute'"
        )
