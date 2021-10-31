from mashumaro.meta.macros import PY_38_MIN

if PY_38_MIN:
    from typing import Literal
else:
    from typing_extensions import Literal  # type: ignore


NamedTupleDeserializationEngine = Literal["as_dict"]
DateTimeDeserializationEngine = Literal["ciso8601", "pendulum"]
AnyDeserializationEngine = Literal[
    NamedTupleDeserializationEngine, DateTimeDeserializationEngine
]

NamedTupleSerializationEngine = Literal["as_dict"]
AnySerializationEngine = NamedTupleSerializationEngine


__all__ = ["AnyDeserializationEngine", "AnySerializationEngine"]
