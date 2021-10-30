from typing import Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


NamedTupleDeserializationEngine = Literal["as_dict"]
DateTimeDeserializationEngine = Literal["ciso8601", "pendulum"]
AnyDeserializationEngine = Union[
    NamedTupleDeserializationEngine, DateTimeDeserializationEngine
]

NamedTupleSerializationEngine = Literal["as_dict"]
AnySerializationEngine = NamedTupleSerializationEngine


__all__ = ["AnyDeserializationEngine", "AnySerializationEngine"]
