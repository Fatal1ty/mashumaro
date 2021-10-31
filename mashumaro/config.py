from typing import Any, Callable, Dict, List, Union

from mashumaro.meta.macros import PEP_586_COMPATIBLE
from mashumaro.types import SerializationStrategy

if PEP_586_COMPATIBLE:
    from typing import Literal  # type: ignore
else:
    from typing_extensions import Literal  # type: ignore


TO_DICT_ADD_BY_ALIAS_FLAG = "TO_DICT_ADD_BY_ALIAS_FLAG"
TO_DICT_ADD_OMIT_NONE_FLAG = "TO_DICT_ADD_OMIT_NONE_FLAG"


CodeGenerationOption = Literal[
    "TO_DICT_ADD_BY_ALIAS_FLAG",
    "TO_DICT_ADD_OMIT_NONE_FLAG",
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


__all__ = [
    "BaseConfig",
    "TO_DICT_ADD_BY_ALIAS_FLAG",
    "TO_DICT_ADD_OMIT_NONE_FLAG",
]
