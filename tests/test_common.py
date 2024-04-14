import dataclasses
from dataclasses import dataclass, field
from enum import Enum
from pathlib import PurePosixPath
from typing import Any, Literal, NamedTuple, Optional

import msgpack
import pytest
from typing_extensions import Self

from mashumaro.config import BaseConfig
from mashumaro.core.const import PY_310_MIN
from mashumaro.core.meta.types.common import clean_id
from mashumaro.mixins.dict import DataClassDictMixin
from mashumaro.mixins.json import DataClassJSONMixin
from mashumaro.mixins.msgpack import DataClassMessagePackMixin
from mashumaro.mixins.yaml import DataClassYAMLMixin
from mashumaro.types import GenericSerializableType, SerializableType


@dataclass
class EntityA1(DataClassDictMixin):
    x: int


@dataclass
class EntityA2(EntityA1):
    y: int


@dataclass
class EntityA1Wrapper(DataClassMessagePackMixin):
    entity: EntityA1


@dataclass
class EntityA2Wrapper(DataClassMessagePackMixin):
    entity: EntityA2


@dataclass
class EntityB1(DataClassDictMixin):
    x: int


@dataclass
class EntityB2(EntityB1):
    y: int


@dataclass
class EntityB1WrapperDict(DataClassDictMixin):
    entity: EntityB1


@dataclass
class EntityB2WrapperMessagePack(DataClassMessagePackMixin):
    entity: EntityB2


@dataclass
class EntityBWrapperMessagePack(DataClassMessagePackMixin):
    entity1wrapper: EntityB1WrapperDict
    entity2wrapper: EntityB2WrapperMessagePack


if PY_310_MIN:

    @dataclass(kw_only=True)
    class DataClassKwOnly1(DataClassDictMixin):
        x: int
        y: int

    @dataclass
    class DataClassKwOnly2(DataClassDictMixin):
        x: int = field(kw_only=True)
        y: int

    @dataclass(kw_only=True)
    class DataClassKwOnly3(DataClassDictMixin):
        x: int
        y: int = field(kw_only=False)

    @dataclass
    class DataClassKwOnly4(DataClassDictMixin):
        x: int
        _: dataclasses.KW_ONLY
        y: int

    @dataclass(kw_only=True)
    class LazyDataClassKwOnly1(DataClassDictMixin):
        x: int
        y: int

        class Config(BaseConfig):
            lazy_compilation = True

    @dataclass
    class LazyDataClassKwOnly2(DataClassDictMixin):
        x: int = field(kw_only=True)
        y: int

        class Config(BaseConfig):
            lazy_compilation = True

    @dataclass(kw_only=True)
    class LazyDataClassKwOnly3(DataClassDictMixin):
        x: int
        y: int = field(kw_only=False)

        class Config(BaseConfig):
            lazy_compilation = True

    @dataclass
    class LazyDataClassKwOnly4(DataClassDictMixin):
        x: int
        _: dataclasses.KW_ONLY
        y: int

        class Config(BaseConfig):
            lazy_compilation = True


@dataclass
class BaseClassWithPosArgs(DataClassDictMixin):
    pos1: int
    pos2: int
    pos3: int


@dataclass
class DerivedClassWithOverriddenMiddlePosArg(BaseClassWithPosArgs):
    kw1: int = 0
    pos2: int


@dataclass
class DerivedClassWithOverriddenMiddlePosArgWithField(BaseClassWithPosArgs):
    kw1: int = 0
    pos2: int = field(metadata={})


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

    class MySerializableType(SerializableType):
        __slots__ = ("number",)

        def __init__(self, number):
            self.number = number

    class MyGenericSerializableType(GenericSerializableType):
        __slots__ = ("number",)

        def __init__(self, number):
            self.number = number

    for cls in (
        RegularDataClass,
        DictDataClass,
        JSONDataClass,
        MessagePackDataClass,
        YAMLDataClass,
        MySerializableType,
        MyGenericSerializableType,
    ):
        instance = cls(1)
        with pytest.raises(AttributeError) as e:
            instance.new_attribute = 2
        assert str(e.value).startswith(
            f"'{cls.__name__}' object has no attribute 'new_attribute'"
        )


def test_data_class_dict_mixin_from_dict():
    assert DataClassDictMixin.from_dict({}) is None


def test_data_class_dict_mixin_to_dict():
    assert DataClassDictMixin().to_dict() is None


def test_compiled_mixin_with_inheritance_1():
    entity = EntityA2(x=1, y=2)
    wrapper = EntityA2Wrapper(entity)
    data = msgpack.packb({"entity": {"x": 1, "y": 2}}, use_bin_type=True)
    assert wrapper.to_msgpack() == data
    assert EntityA2Wrapper.from_msgpack(data) == wrapper


def test_compiled_mixin_with_inheritance_2():
    entity1w = EntityB1WrapperDict(EntityB1(x=1))
    entity2w = EntityB2WrapperMessagePack(EntityB2(x=1, y=2))
    wrapper = EntityBWrapperMessagePack(entity1w, entity2w)
    data = msgpack.packb(
        {
            "entity1wrapper": {"entity": {"x": 1}},
            "entity2wrapper": {"entity": {"x": 1, "y": 2}},
        },
        use_bin_type=True,
    )
    assert wrapper.to_msgpack() == data
    assert EntityBWrapperMessagePack.from_msgpack(data) == wrapper


@pytest.mark.skipif(not PY_310_MIN, reason="requires python 3.10+")
def test_kw_only_dataclasses():
    data = {"x": "1", "y": "2"}
    for cls in (
        DataClassKwOnly1,
        DataClassKwOnly2,
        DataClassKwOnly3,
        DataClassKwOnly4,
        LazyDataClassKwOnly1,
        LazyDataClassKwOnly2,
        LazyDataClassKwOnly3,
        LazyDataClassKwOnly4,
    ):
        obj = cls.from_dict(data)
        assert obj.x == 1
        assert obj.y == 2


def test_kw_args_when_pos_arg_is_overridden_without_field():
    obj = DerivedClassWithOverriddenMiddlePosArg(1, 2, 3, 4)
    loaded = DerivedClassWithOverriddenMiddlePosArg.from_dict(
        {"pos1": "1", "pos2": "2", "pos3": "3", "kw1": "4"}
    )
    assert loaded == obj
    assert loaded.pos1 == 1
    assert loaded.pos2 == 2
    assert loaded.pos3 == 3
    assert loaded.kw1 == 4


def test_kw_args_when_pos_arg_is_overridden_with_field():
    obj = DerivedClassWithOverriddenMiddlePosArgWithField(1, 2, 3, 4)
    loaded = DerivedClassWithOverriddenMiddlePosArgWithField.from_dict(
        {"pos1": "1", "pos2": "2", "pos3": "3", "kw1": "4"}
    )
    assert loaded == obj
    assert loaded.pos1 == 1
    assert loaded.pos2 == 2
    assert loaded.pos3 == 3
    assert loaded.kw1 == 4


def test_local_types():
    @dataclass
    class LocalDataclassType:
        foo: int

    class LocalNamedTupleType(NamedTuple):
        foo: int

    class LocalPathLike(PurePosixPath):
        pass

    class LocalEnumType(Enum):
        FOO = "foo"

    class LocalSerializableType(SerializableType):
        @classmethod
        def _deserialize(cls, value):
            return LocalSerializableType()

        def _serialize(self) -> Any:
            return {}

        def __eq__(self, __value: object) -> bool:
            return isinstance(__value, LocalSerializableType)

    class LocalGenericSerializableType(GenericSerializableType):
        @classmethod
        def _deserialize(cls, value, types):
            return LocalGenericSerializableType()

        def _serialize(self, types) -> Any:
            return {}

        def __eq__(self, __value: object) -> bool:
            return isinstance(__value, LocalGenericSerializableType)

    class LocalSelfSerializableAnnotatedType(
        SerializableType, use_annotations=True
    ):
        @classmethod
        def _deserialize(cls, value: Self) -> Self:
            return value

        def _serialize(self) -> Self:
            return self

        def __eq__(self, __value: object) -> bool:
            return isinstance(__value, LocalSelfSerializableAnnotatedType)

    @dataclass
    class DataClassWithLocalType(DataClassDictMixin):
        x1: LocalDataclassType
        x2: LocalNamedTupleType
        x3: LocalPathLike
        x4: LocalEnumType
        x4_1: Literal[LocalEnumType.FOO]
        x5: LocalSerializableType
        x6: LocalGenericSerializableType
        x7: Optional[Self]
        x8: LocalSelfSerializableAnnotatedType

    obj = DataClassWithLocalType(
        x1=LocalDataclassType(foo=0),
        x2=LocalNamedTupleType(foo=0),
        x3=LocalPathLike("path/to/file"),
        x4=LocalEnumType.FOO,
        x4_1=LocalEnumType.FOO,
        x5=LocalSerializableType(),
        x6=LocalGenericSerializableType(),
        x7=None,
        x8=LocalSelfSerializableAnnotatedType(),
    )
    assert obj.to_dict() == {
        "x1": {"foo": 0},
        "x2": [0],
        "x3": "path/to/file",
        "x4": "foo",
        "x4_1": "foo",
        "x5": {},
        "x6": {},
        "x7": None,
        "x8": LocalSelfSerializableAnnotatedType(),
    }
    assert (
        DataClassWithLocalType.from_dict(
            {
                "x1": {"foo": 0},
                "x2": [0],
                "x3": "path/to/file",
                "x4": "foo",
                "x4_1": "foo",
                "x5": {},
                "x6": {},
                "x7": None,
                "x8": LocalSelfSerializableAnnotatedType(),
            }
        )
        == obj
    )


def test_clean_id():
    assert clean_id("") == "_"
    assert clean_id("foo") == "foo"
    assert clean_id("foo.<locals>.bar") == "foo__locals__bar"
