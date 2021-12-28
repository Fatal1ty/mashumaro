from typing import Any, Callable, Dict, Union

from mashumaro.types import SerializationStrategy

SerializationStrategyValueType = Union[
    SerializationStrategy, Dict[str, Union[str, Callable]]
]


class Dialect:
    serialization_strategy: Dict[Any, SerializationStrategyValueType] = {}


__all__ = ["Dialect"]
