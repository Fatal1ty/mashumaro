from typing import Any, Callable, Optional, Union

from typing_extensions import Literal

from mashumaro.types import SerializationStrategy

NamedTupleDeserializationEngine = Literal["as_dict", "as_list"]
DateTimeDeserializationEngine = Literal["ciso8601", "pendulum"]
AnyDeserializationEngine = Literal[
    NamedTupleDeserializationEngine, DateTimeDeserializationEngine
]

NamedTupleSerializationEngine = Literal["as_dict", "as_list"]
AnySerializationEngine = NamedTupleSerializationEngine


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
