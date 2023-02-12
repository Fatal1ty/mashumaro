from dataclasses import dataclass
from typing import Generic, List, Sequence, TypeVar

from mashumaro import DataClassDictMixin
from mashumaro.types import SerializationStrategy

T = TypeVar("T")


class TruncatedListSerializationStrategy(SerializationStrategy, Generic[T]):
    def serialize(self, value: List[T]) -> Sequence[T]:
        return value[:-1]

    def deserialize(self, value: Sequence[T]) -> Sequence[T]:
        return value[:-1]


def test_generic_list_serialization_strategy():
    @dataclass
    class MyDataClass(DataClassDictMixin):
        x: List[int]
        y: List[List[int]]

        class Config:
            serialization_strategy = {
                list: TruncatedListSerializationStrategy()
            }

    obj = MyDataClass([1, 2, 3, 4, 5], [[1, 2], [3, 4]])
    assert obj.to_dict() == {"x": [1, 2, 3, 4], "y": [[1]]}
    assert MyDataClass.from_dict(
        {"x": ["1", "2", "3", "4"], "y": [[1, 2], [3, 4]]}
    ) == MyDataClass([1, 2, 3], [[1]])
