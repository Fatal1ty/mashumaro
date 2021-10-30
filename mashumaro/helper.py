from typing import Any, Callable, Optional, Union

from mashumaro.types import SerializationStrategy
from mashumaro.typing import AnyDeserializationEngine, AnySerializationEngine


def field_options(
    serialize: Optional[
        Union[AnySerializationEngine, Callable[[Any], Any]]
    ] = None,
    deserialize: Optional[
        Union[AnyDeserializationEngine, Callable[[Any], Any]]
    ] = None,
    serialization_strategy: Optional[SerializationStrategy] = None,
    alias: Optional[str] = None,
):
    return {
        "serialize": serialize,
        "deserialize": deserialize,
        "serialization_strategy": serialization_strategy,
        "alias": alias,
    }


__all__ = ["field_options"]
