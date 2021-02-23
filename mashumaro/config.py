from typing import Any, Callable, Dict, List, Union

from mashumaro.types import SerializationStrategy

TO_DICT_ADD_OMIT_NONE_FLAG = "TO_DICT_ADD_OMIT_NONE_FLAG"


SerializationStrategyValueType = Union[
    SerializationStrategy, Dict[str, Union[str, Callable]]
]


class BaseConfig:
    debug: bool = False
    code_generation_options: List[str] = []
    serialization_strategy: Dict[Any, SerializationStrategyValueType] = {}
