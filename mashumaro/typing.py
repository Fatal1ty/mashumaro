try:
    from typing import Literal  # type: ignore
except ImportError:
    from typing_extensions import Literal  # type: ignore


NamedTupleDeserializationEngine = Literal["as_dict"]
DateTimeDeserializationEngine = Literal["ciso8601", "pendulum"]
AnyDeserializationEngine = Literal[
    NamedTupleDeserializationEngine, DateTimeDeserializationEngine
]

NamedTupleSerializationEngine = Literal["as_dict"]
AnySerializationEngine = NamedTupleSerializationEngine


__all__ = ["AnyDeserializationEngine", "AnySerializationEngine"]
