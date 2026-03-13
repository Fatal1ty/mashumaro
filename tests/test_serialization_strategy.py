import enum
from dataclasses import dataclass, field
from datetime import date
from typing import Generic, List, Sequence, TypeVar

from mashumaro import DataClassDictMixin, field_options
from mashumaro.types import SerializationStrategy

T = TypeVar("T")


class TruncatedGenericListSerializationStrategy(
    SerializationStrategy, Generic[T]
):
    def serialize(self, value: List[T]) -> Sequence[T]:
        return value[:-1]

    def deserialize(self, value: Sequence[T]) -> Sequence[T]:
        return value[:-1]


class TruncatedAnnotatedDateListSerializationStrategy(
    SerializationStrategy, use_annotations=True
):
    def serialize(self, value) -> Sequence[date]:
        return value[:-1]

    def deserialize(self, value: Sequence[date]):
        return value[:-1]


class TruncatedDateListSerializationStrategy(SerializationStrategy):
    def serialize(self, value) -> Sequence[date]:
        return value[:-1]

    def deserialize(self, value: Sequence[date]):
        return value[:-1]


class TruncatedUnannotatedListSerializationStrategy(
    SerializationStrategy, use_annotations=True
):
    def serialize(self, value):
        return value[:-1]

    def deserialize(self, value):
        return value[:-1]


def test_generic_list_serialization_strategy():
    @dataclass
    class MyDataClass(DataClassDictMixin):
        x: List[int]
        y: List[List[int]]

        class Config:
            serialization_strategy = {
                list: TruncatedGenericListSerializationStrategy()
            }

    obj = MyDataClass([1, 2, 3, 4, 5], [[1, 2], [3, 4]])
    assert obj.to_dict() == {"x": [1, 2, 3, 4], "y": [[1]]}
    assert MyDataClass.from_dict(
        {"x": ["1", "2", "3", "4"], "y": [[1, 2], [3, 4]]}
    ) == MyDataClass([1, 2, 3], [[1]])


def test_date_list_serialization_strategy_with_use_annotations():
    @dataclass
    class MyDataClass(DataClassDictMixin):
        x: List[date]

        class Config:
            serialization_strategy = {
                list: TruncatedAnnotatedDateListSerializationStrategy()
            }

    obj = MyDataClass(
        [
            date(2023, 2, 12),
            date(2023, 2, 12),
            date(2023, 2, 12),
            date(2023, 2, 12),
            date(2023, 2, 12),
        ]
    )
    assert obj.to_dict() == {
        "x": ["2023-02-12", "2023-02-12", "2023-02-12", "2023-02-12"]
    }
    assert MyDataClass.from_dict(
        {"x": ["2023-02-12", "2023-02-12", "2023-02-12", "2023-02-12"]}
    ) == MyDataClass([date(2023, 2, 12), date(2023, 2, 12), date(2023, 2, 12)])


def test_date_list_serialization_strategy_without_use_annotations():
    @dataclass
    class MyDataClass(DataClassDictMixin):
        x: List[date]

        class Config:
            serialization_strategy = {
                list: TruncatedDateListSerializationStrategy()
            }

    obj = MyDataClass(
        [
            date(2023, 2, 12),
            date(2023, 2, 12),
            date(2023, 2, 12),
            date(2023, 2, 12),
            date(2023, 2, 12),
        ]
    )
    assert obj.to_dict() == {
        "x": [
            date(2023, 2, 12),
            date(2023, 2, 12),
            date(2023, 2, 12),
            date(2023, 2, 12),
        ]
    }
    assert MyDataClass.from_dict(
        {"x": ["2023-02-12", "2023-02-12", "2023-02-12", "2023-02-12"]}
    ) == MyDataClass(["2023-02-12", "2023-02-12", "2023-02-12"])


def test_date_list_serialization_strategy_use_annotations_without_annotations():
    @dataclass
    class MyDataClass(DataClassDictMixin):
        x: List[date]

        class Config:
            serialization_strategy = {
                list: TruncatedUnannotatedListSerializationStrategy()
            }

    obj = MyDataClass(
        [
            date(2023, 2, 12),
            date(2023, 2, 12),
            date(2023, 2, 12),
            date(2023, 2, 12),
            date(2023, 2, 12),
        ]
    )
    assert obj.to_dict() == {
        "x": [
            date(2023, 2, 12),
            date(2023, 2, 12),
            date(2023, 2, 12),
            date(2023, 2, 12),
        ]
    }
    assert MyDataClass.from_dict(
        {"x": ["2023-02-12", "2023-02-12", "2023-02-12", "2023-02-12"]}
    ) == MyDataClass(["2023-02-12", "2023-02-12", "2023-02-12"])


def test_date_list_field_serialization_strategy_with_use_annotations():
    @dataclass
    class MyDataClass(DataClassDictMixin):
        x: List[date] = field(
            metadata=field_options(
                serialization_strategy=(
                    TruncatedAnnotatedDateListSerializationStrategy()
                )
            )
        )

    obj = MyDataClass(
        [
            date(2023, 2, 12),
            date(2023, 2, 12),
            date(2023, 2, 12),
            date(2023, 2, 12),
            date(2023, 2, 12),
        ]
    )
    assert obj.to_dict() == {
        "x": ["2023-02-12", "2023-02-12", "2023-02-12", "2023-02-12"]
    }
    assert MyDataClass.from_dict(
        {"x": ["2023-02-12", "2023-02-12", "2023-02-12", "2023-02-12"]}
    ) == MyDataClass([date(2023, 2, 12), date(2023, 2, 12), date(2023, 2, 12)])


class EnumByNameStrategy(SerializationStrategy, match_subclasses=True):
    def serialize(self, value: enum.Enum) -> str:
        return value.name

    def deserialize(self, value: str) -> enum.Enum:
        raise NotImplementedError


class MyEnum(enum.Enum):
    A = 1
    B = 2


class MyIntEnum(enum.IntEnum):
    X = 10
    Y = 20


def test_serialization_strategy_match_subclasses():

    @dataclass
    class MyDataClass(DataClassDictMixin):
        e: MyEnum

        class Config:
            serialization_strategy = {enum.Enum: EnumByNameStrategy()}

    obj = MyDataClass(e=MyEnum.A)
    assert obj.to_dict() == {"e": "A"}


def test_serialization_strategy_match_subclasses_specific_overrides_base():
    class IntEnumByValueStrategy(SerializationStrategy, match_subclasses=True):
        def serialize(self, value: enum.IntEnum) -> int:
            return value.value * 100

        def deserialize(self, value: int) -> enum.IntEnum:
            raise NotImplementedError

    @dataclass
    class MyDataClass(DataClassDictMixin):
        e1: MyEnum
        e2: MyIntEnum

        class Config:
            serialization_strategy = {
                enum.Enum: EnumByNameStrategy(),
                enum.IntEnum: IntEnumByValueStrategy(),
            }

    obj = MyDataClass(e1=MyEnum.B, e2=MyIntEnum.X)
    result = obj.to_dict()
    assert result["e1"] == "B"
    assert result["e2"] == 1000


def test_serialization_strategy_no_match_subclasses_by_default():

    class DefaultStrategy(SerializationStrategy):
        def serialize(self, value: enum.Enum) -> str:
            return value.name

        def deserialize(self, value: str) -> enum.Enum:
            raise NotImplementedError

    @dataclass
    class MyDataClass(DataClassDictMixin):
        e: MyEnum

        class Config:
            serialization_strategy = {enum.Enum: DefaultStrategy()}

    obj = MyDataClass(e=MyEnum.A)
    assert obj.to_dict() == {"e": 1}
