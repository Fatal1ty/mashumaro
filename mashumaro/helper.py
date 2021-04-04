from typing import Any, Callable, Optional, Union

from mashumaro.types import SerializationStrategy


def field_options(
    serialize: Optional[Callable[[Any], Any]] = None,
    deserialize: Optional[Union[str, Callable[[Any], Any]]] = None,
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
