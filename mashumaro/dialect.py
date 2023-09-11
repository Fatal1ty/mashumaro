from typing import Any, Callable, Dict, Sequence, Union

from typing_extensions import Literal

from mashumaro.core.const import Sentinel
from mashumaro.types import SerializationStrategy

__all__ = ["Dialect"]


SerializationStrategyValueType = Union[
    SerializationStrategy, Dict[str, Union[str, Callable]]
]


class Dialect:
    serialization_strategy: Dict[Any, SerializationStrategyValueType] = {}
    omit_none: Union[bool, Literal[Sentinel.MISSING]] = Sentinel.MISSING
    omit_default: Union[bool, Literal[Sentinel.MISSING]] = Sentinel.MISSING
    no_copy_collections: Sequence[Any] = tuple()
