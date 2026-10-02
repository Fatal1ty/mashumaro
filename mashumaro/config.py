from collections.abc import Callable, Mapping, Sequence
from types import MappingProxyType
from typing import Any, Literal, TypedDict

from mashumaro.core.const import Sentinel
from mashumaro.dialect import Dialect
from mashumaro.types import Discriminator, SerializationStrategy

__all__ = [
    "ADD_DIALECT_SUPPORT",
    "ADD_SERIALIZATION_CONTEXT",
    "TO_DICT_ADD_BY_ALIAS_FLAG",
    "TO_DICT_ADD_OMIT_NONE_FLAG",
    "BaseConfig",
    "SerializationStrategyValueType",
]


TO_DICT_ADD_BY_ALIAS_FLAG = "TO_DICT_ADD_BY_ALIAS_FLAG"
TO_DICT_ADD_OMIT_NONE_FLAG = "TO_DICT_ADD_OMIT_NONE_FLAG"
ADD_DIALECT_SUPPORT = "ADD_DIALECT_SUPPORT"
ADD_SERIALIZATION_CONTEXT = "ADD_SERIALIZATION_CONTEXT"


CodeGenerationOption = Literal[
    "TO_DICT_ADD_BY_ALIAS_FLAG",
    "TO_DICT_ADD_OMIT_NONE_FLAG",
    "ADD_DIALECT_SUPPORT",
    "ADD_SERIALIZATION_CONTEXT",
]


class SerializationStrategyDict(TypedDict, total=False):
    serialize: str | Callable
    deserialize: str | Callable


SerializationStrategyValueType = (
    SerializationStrategy | SerializationStrategyDict
)


class BaseConfig:
    debug: bool = False
    code_generation_options: Sequence[CodeGenerationOption] = ()
    serialization_strategy: Mapping[Any, SerializationStrategyValueType] = (
        MappingProxyType({})
    )
    aliases: Mapping[str, str | Sequence[str]] = MappingProxyType({})
    serialize_by_alias: bool | Literal[Sentinel.MISSING] = Sentinel.MISSING
    namedtuple_as_dict: bool | Literal[Sentinel.MISSING] = Sentinel.MISSING
    allow_postponed_evaluation: bool = True
    dialect: type[Dialect] | None = None
    omit_none: bool | Literal[Sentinel.MISSING] = Sentinel.MISSING
    omit_default: bool | Literal[Sentinel.MISSING] = Sentinel.MISSING
    orjson_options: int | None = 0
    json_schema: Mapping[str, Any] = MappingProxyType({})
    discriminator: Discriminator | None = None
    lazy_compilation: bool = False
    sort_keys: bool = False
    allow_deserialization_not_by_alias: bool = False
    forbid_extra_keys: bool = False
