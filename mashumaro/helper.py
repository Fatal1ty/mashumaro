from collections.abc import Callable
from typing import Any, TypeVar

from typing_extensions import Literal

from mashumaro.types import SerializationStrategy

__all__ = ["field_options", "pass_through"]


NamedTupleDeserializationEngine = Literal["as_dict", "as_list"]
DateTimeDeserializationEngine = Literal["ciso8601", "pendulum"]
AnyDeserializationEngine = Literal[
    NamedTupleDeserializationEngine, DateTimeDeserializationEngine
]

NamedTupleSerializationEngine = Literal["as_dict", "as_list"]
OmitSerializationEngine = Literal["omit"]
AnySerializationEngine = (
    NamedTupleSerializationEngine | OmitSerializationEngine
)


T = TypeVar("T")


def field_options(
    serialize: AnySerializationEngine | Callable[[Any], Any] | None = None,
    deserialize: AnyDeserializationEngine | Callable[[Any], Any] | None = None,
    serialization_strategy: SerializationStrategy | None = None,
    alias: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    return {
        "serialize": serialize,
        "deserialize": deserialize,
        "serialization_strategy": serialization_strategy,
        "alias": alias,
        **kwargs,
    }


class _PassThrough(SerializationStrategy):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

    def serialize(self, value: T) -> T:
        return value

    def deserialize(self, value: T) -> T:
        return value


pass_through = _PassThrough()
