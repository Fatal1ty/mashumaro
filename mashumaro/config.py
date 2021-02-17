from typing import List

TO_DICT_ADD_OMIT_NONE_FLAG = "TO_DICT_ADD_OMIT_NONE_FLAG"


class BaseConfig:
    debug: bool = False
    code_generation_options: List[str] = []
