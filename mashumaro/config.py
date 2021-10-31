from typing import Any, Callable, Dict, List, Union

from mashumaro.meta.macros import PY_38_MIN
from mashumaro.types import SerializationStrategy

if PY_38_MIN:
    from typing import Literal
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


__all__ = [
    "BaseConfig",
    "TO_DICT_ADD_BY_ALIAS_FLAG",
    "TO_DICT_ADD_OMIT_NONE_FLAG",
]
