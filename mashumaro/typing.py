from mashumaro.meta.macros import PEP_586_COMPATIBLE

if PEP_586_COMPATIBLE:  # type: ignore
    from typing import Literal  # type: ignore
else:
    from typing_extensions import Literal  # type: ignore


NamedTupleDeserializationEngine = Literal["as_dict", "as_list"]
DateTimeDeserializationEngine = Literal["ciso8601", "pendulum"]
AnyDeserializationEngine = Literal[
    NamedTupleDeserializationEngine, DateTimeDeserializationEngine
]

NamedTupleSerializationEngine = Literal["as_dict", "as_list"]
AnySerializationEngine = NamedTupleSerializationEngine


__all__ = ["AnyDeserializationEngine", "AnySerializationEngine"]
