from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig

from mashumaro.types import SerializationStrategy


def test_postponed_serialization_strategy() -> None:
    class Strategy(SerializationStrategy, use_annotations=True):
        def serialize(self, value) -> dict[str, Any]:
            return {"a": value}

        def deserialize(self, value: dict[str, Any]):
            return value.get("a")

    @dataclass
    class MyDataClass(DataClassDictMixin):
        x: Optional[int]

        class Config(BaseConfig):
            serialization_strategy = {int: Strategy()}

    obj = MyDataClass(x=2)
    assert obj.to_dict() == {"x": {"a": 2}}
    assert MyDataClass.from_dict({"x": {"a": 2}}) == obj
