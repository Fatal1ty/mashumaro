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
