from dataclasses import dataclass

import msgpack
import pytest

from mashumaro.mixins.dict import DataClassDictMixin
from mashumaro.mixins.json import DataClassJSONMixin
from mashumaro.mixins.msgpack import DataClassMessagePackMixin
from mashumaro.mixins.yaml import DataClassYAMLMixin


@dataclass
class Entity1(DataClassDictMixin):
    x: int


@dataclass
class Entity2(Entity1):
    y: int


@dataclass
class Entity1Wrapper(DataClassMessagePackMixin):
    entity: Entity1


@dataclass
class Entity2Wrapper(DataClassMessagePackMixin):
    entity: Entity2


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


def test_data_class_dict_mixin_from_dict():
    assert DataClassDictMixin.from_dict({}) is None


def test_data_class_dict_mixin_to_dict():
    assert DataClassDictMixin().to_dict() is None


def test_compiled_mixin_with_inheritance():
    entity = Entity2(x=1, y=2)
    wrapper = Entity2Wrapper(entity)
    data = msgpack.packb({"entity": {"x": 1, "y": 2}}, use_bin_type=True)
    assert wrapper.to_msgpack() == data
    assert Entity2Wrapper.from_msgpack(data) == wrapper
