from dataclasses import dataclass
from datetime import date
from typing import Any, Generic, Iterator, Mapping, Tuple, TypeVar

import pytest
from typing_extensions import Self

from mashumaro import DataClassDictMixin
from mashumaro.exceptions import UnserializableField
from mashumaro.types import Alias, SerializableType
from tests.entities import GenericSerializableList, GenericSerializableWrapper

XT = TypeVar("XT")
YT = TypeVar("YT")


class MySerializableType(SerializableType):
    def __init__(self, value):
        self.value = value

    def _serialize(self):
        return self.value.isoformat()

    @classmethod
    def _deserialize(cls, value):
        return cls(date.fromisoformat(value))


class MyAnnotatedSerializableType(SerializableType, use_annotations=True):
    def __init__(self, value: date):
        self.value = value

    def _serialize(self) -> date:
        return self.value

    @classmethod
    def _deserialize(cls, value: date):
        return cls(value)


class MyAnnotatedSerializableTypeWithoutAnnotationsInDeserialize(
    SerializableType, use_annotations=True
):
    def __init__(self, value):  # pragma: no cover
        self.value = value

    def _serialize(self) -> date:  # pragma: no cover
        return self.value

    @classmethod
    def _deserialize(cls, value):  # pragma: no cover
        return cls(value)


class MyAnnotatedSerializableTypeWithoutAnnotationsInSerialize(
    SerializableType, use_annotations=True
):
    def __init__(self, value):  # pragma: no cover
        self.value = value

    def _serialize(self):  # pragma: no cover
        return self.value

    @classmethod
    def _deserialize(cls, value: date):  # pragma: no cover
        return cls(value)


class MyAnnotatedGenericSerializableType(
    Generic[XT, YT], SerializableType, use_annotations=True
):
    def __init__(self, value: Tuple[XT, YT]):
        self.value = value

    def _serialize(self) -> Tuple[YT, XT]:
        return tuple(reversed(self.value))

    @classmethod
    def _deserialize(cls, value: Tuple[XT, YT]):
        return cls(value)


class MyAnnotatedGenericSerializableTypeWithMixedTypeVars(
    Generic[XT], SerializableType, use_annotations=True
):
    def __init__(self, value):
        self.value = value

    def _serialize(self) -> Tuple[int, XT, float]:
        return self.value

    @classmethod
    def _deserialize(cls, value: Tuple[int, XT, float]):
        return cls(value)


class MyAnnotatedGenericPEP585SerializableType(
    Generic[XT, YT], SerializableType, use_annotations=True
):
    def __init__(self, value: tuple[XT, YT]):
        self.value = value

    def _serialize(self) -> tuple[YT, XT]:
        return tuple(reversed(self.value))

    @classmethod
    def _deserialize(cls, value: tuple[XT, YT]):
        return cls(value)


class MyMapping(Mapping[XT, YT], SerializableType, use_annotations=True):
    def __init__(self, value: Mapping[Any, Any]):
        self.value = value

    def _serialize(self) -> Mapping[XT, YT]:
        return self.value

    @classmethod
    def _deserialize(cls, mapping: Mapping[XT, YT]):
        return cls(mapping)

    def __getitem__(self, __k: XT) -> YT:
        return self.value[__k]

    def __len__(self) -> int:  # pragma: no cover
        return len(self.value)

    def __iter__(self) -> Iterator[XT]:
        return iter(self.value)

    def __repr__(self):  # pragma: no cover
        return f"<MyMapping: {repr(self.value)}>"


class MyAnnotatedUserGenericSerializableType(
    Generic[XT, YT], SerializableType, use_annotations=True
):
    def __init__(self, value: MyMapping[XT, YT]):
        self.value = value

    def _serialize(self) -> MyMapping[XT, YT]:
        return self.value

    @classmethod
    def _deserialize(cls, value: MyMapping[XT, YT]):
        return cls(value)

    def __repr__(self):  # pragma: no cover
        return f"<MyAnnotatedUserGenericSerializableType: {repr(self.value)}>"


class MySelfSerializableType(SerializableType, use_annotations=True):
    def _serialize(self) -> Self:
        return self

    @classmethod
    def _deserialize(cls, value: Self) -> Self:
        return value


def test_generic_serializable_list_int():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: GenericSerializableList[int]

    obj = DataClass(x=GenericSerializableList([1, 2, 3]))
    assert DataClass.from_dict({"x": [3, 4, 5]}) == obj
    assert obj.to_dict() == {"x": [3, 4, 5]}


def test_generic_serializable_list_str():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: GenericSerializableList[str]

    obj = DataClass(x=GenericSerializableList(["a", "b", "c"]))
    assert DataClass.from_dict({"x": ["_a", "_b", "_c"]}) == obj
    assert obj.to_dict() == {"x": ["_a", "_b", "_c"]}


def test_generic_serializable_wrapper_with_type_from_another_module():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: GenericSerializableWrapper[date]

    obj = DataClass(x=GenericSerializableWrapper(date(2022, 12, 8)))
    assert DataClass.from_dict({"x": "2022-12-08"}) == obj
    assert obj.to_dict() == {"x": "2022-12-08"}


def test_simple_serializable_type():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MySerializableType

    obj = DataClass.from_dict({"x": "2022-12-07"})
    assert obj.x.value == date(2022, 12, 7)
    assert obj.to_dict() == {"x": "2022-12-07"}


def test_annotated_serializable_type():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyAnnotatedSerializableType

    obj = DataClass.from_dict({"x": "2022-12-07"})
    assert obj.x.value == date(2022, 12, 7)
    assert obj.to_dict() == {"x": "2022-12-07"}


def test_annotated_serializable_type_without_annotations_in_deserialize():
    with pytest.raises(UnserializableField) as e:

        @dataclass
        class _(DataClassDictMixin):
            x: MyAnnotatedSerializableTypeWithoutAnnotationsInDeserialize

    assert (
        e.value.msg
        == 'Method _deserialize must have annotated "value" argument'
    )


def test_annotated_serializable_type_without_annotations_in_serialize():
    with pytest.raises(UnserializableField) as e:

        @dataclass
        class _(DataClassDictMixin):
            x: MyAnnotatedSerializableTypeWithoutAnnotationsInSerialize

    assert e.value.msg == "Method _serialize must have return annotation"


def test_annotated_generic_serializable_type():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyAnnotatedGenericSerializableType

    obj = DataClass.from_dict({"x": ["2022-12-07", "3.14"]})
    assert obj.x.value == ("2022-12-07", "3.14")
    assert obj.to_dict() == {"x": ["3.14", "2022-12-07"]}

    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyAnnotatedGenericSerializableType[date, float]

    obj = DataClass.from_dict({"x": ["2022-12-07", "3.14"]})
    assert obj.x.value == (date(2022, 12, 7), 3.14)
    assert obj.to_dict() == {"x": [3.14, "2022-12-07"]}

    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyAnnotatedGenericSerializableType[date, YT]

    obj = DataClass.from_dict({"x": ["2022-12-07", "3.14"]})
    assert obj.x.value == (date(2022, 12, 7), "3.14")
    assert obj.to_dict() == {"x": ["3.14", "2022-12-07"]}


def test_annotated_generic_pep585_serializable_type():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyAnnotatedGenericPEP585SerializableType

    obj = DataClass.from_dict({"x": ["2022-12-07", "3.14"]})
    assert obj.x.value == ("2022-12-07", "3.14")
    assert obj.to_dict() == {"x": ["3.14", "2022-12-07"]}

    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyAnnotatedGenericSerializableType[date, float]

    obj = DataClass.from_dict({"x": ["2022-12-07", "3.14"]})
    assert obj.x.value == (date(2022, 12, 7), 3.14)
    assert obj.to_dict() == {"x": [3.14, "2022-12-07"]}

    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyAnnotatedGenericSerializableType[date, YT]

    obj = DataClass.from_dict({"x": ["2022-12-07", "3.14"]})
    assert obj.x.value == (date(2022, 12, 7), "3.14")
    assert obj.to_dict() == {"x": ["3.14", "2022-12-07"]}


def test_annotated_user_generic_serializable_type():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyAnnotatedUserGenericSerializableType

    obj = DataClass.from_dict({"x": {"2022-12-07": "3.14"}})
    assert type(obj.x.value) is MyMapping
    assert dict(obj.x.value) == {"2022-12-07": "3.14"}
    assert obj.to_dict() == {"x": {"2022-12-07": "3.14"}}

    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyAnnotatedUserGenericSerializableType[date, float]

    obj = DataClass.from_dict({"x": {"2022-12-07": "3.14"}})
    assert type(obj.x.value) is MyMapping
    assert dict(obj.x.value) == {date(2022, 12, 7): 3.14}
    assert obj.to_dict() == {"x": {"2022-12-07": 3.14}}

    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyAnnotatedUserGenericSerializableType[date, YT]

    obj = DataClass.from_dict({"x": {"2022-12-07": "3.14"}})
    assert type(obj.x.value) is MyMapping
    assert dict(obj.x.value) == {date(2022, 12, 7): "3.14"}
    assert obj.to_dict() == {"x": {"2022-12-07": "3.14"}}


def test_serializable_type_inheritance():
    class MySerializableType2(MySerializableType, use_annotations=True):
        pass

    assert MySerializableType2.__use_annotations__

    class MySerializableType3(MySerializableType2):
        pass

    assert MySerializableType3.__use_annotations__

    class MySerializableType4(MySerializableType3, use_annotations=False):
        pass

    assert not MySerializableType4.__use_annotations__


def test_serializable_type_with_self():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MySelfSerializableType

    obj = DataClass(MySelfSerializableType())
    assert obj.to_dict() == {"x": obj.x}
    assert DataClass.from_dict({"x": obj.x}) == obj


def test_annotated_generic_serializable_type_with_mixed_type_vars():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: MyAnnotatedGenericSerializableTypeWithMixedTypeVars[date]

    obj = DataClass.from_dict({"x": ["1", "2022-05-29", "2.3"]})
    # assert obj.x.value == (1, date(2022, 5, 29), 2.3)
    assert obj.to_dict() == {"x": [1, "2022-05-29", 2.3]}


def test_alias():
    x1 = Alias("x")
    x2 = Alias("x")
    y = Alias("y")

    assert x1 == x2
    assert hash(x1) == hash(x2)

    assert x1 != y
    assert x1 != "x"
    assert hash(x1) != hash(y)

    assert str(y) == "Alias(name='y')"
    assert repr(y) == "Alias(name='y')"
