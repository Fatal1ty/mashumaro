from typing import Any, Callable, Dict, List, Optional, Type, Union

from mashumaro.core.const import PEP_586_COMPATIBLE, Sentinel
from mashumaro.dialect import Dialect
from mashumaro.types import SerializationStrategy

if PEP_586_COMPATIBLE:
    from typing import Literal  # type: ignore
else:
    from typing_extensions import Literal  # type: ignore


__all__ = [
    "BaseConfig",
    "TO_DICT_ADD_BY_ALIAS_FLAG",
    "TO_DICT_ADD_OMIT_NONE_FLAG",
    "ADD_DIALECT_SUPPORT",
    "SerializationStrategyValueType",
]


TO_DICT_ADD_BY_ALIAS_FLAG = "TO_DICT_ADD_BY_ALIAS_FLAG"
TO_DICT_ADD_OMIT_NONE_FLAG = "TO_DICT_ADD_OMIT_NONE_FLAG"
ADD_DIALECT_SUPPORT = "ADD_DIALECT_SUPPORT"


CodeGenerationOption = Literal[
    "TO_DICT_ADD_BY_ALIAS_FLAG",
    "TO_DICT_ADD_OMIT_NONE_FLAG",
    "ADD_DIALECT_SUPPORT",
]


SerializationStrategyValueType = Union[
    SerializationStrategy, Dict[str, Union[str, Callable]]
]


class BaseConfig:
    debug: bool = False
    code_generation_options: List[CodeGenerationOption] = []  # type: ignore
    serialization_strategy: Dict[Any, SerializationStrategyValueType] = {}
    aliases: Dict[str, str] = {}
    serialize_by_alias: bool = False
    namedtuple_as_dict: bool = False
    allow_postponed_evaluation: bool = True
    dialect: Optional[Type[Dialect]] = None
    omit_none: Union[bool, Literal[Sentinel.MISSING]] = Sentinel.MISSING
    orjson_options: Optional[int] = 0
    json_schema: Dict[str, Any] = {}
