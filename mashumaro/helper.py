from typing import Any, Callable, Optional, Union

from mashumaro.types import SerializationStrategy


def field_options(
    serialize: Optional[Callable[[Any], Any]] = None,
    deserialize: Optional[Union[str, Callable[[Any], Any]]] = None,
    serialization_strategy: Optional[SerializationStrategy] = None,
):
    return {
        "serialize": serialize,
        "deserialize": deserialize,
        "serialization_strategy": serialization_strategy,
    }


__all__ = ["field_options"]
