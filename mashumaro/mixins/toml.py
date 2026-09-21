from collections.abc import Callable
from datetime import date, datetime, time
from typing import Any, final

import tomli_w
from typing_extensions import Self

from mashumaro.dialect import Dialect
from mashumaro.helper import pass_through
from mashumaro.mixins.dict import DataClassDictMixin

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore


EncodedData = str
Encoder = Callable[[Any], EncodedData]
Decoder = Callable[[EncodedData], dict[Any, Any]]


class TOMLDialect(Dialect):
    no_copy_collections = (list, dict)
    omit_none = True
    serialization_strategy = {
        datetime: pass_through,
        date: pass_through,
        time: pass_through,
    }


class DataClassTOMLMixin(DataClassDictMixin):
    __slots__ = ()

    __mashumaro_builder_params = {
        "packer": {
            "format_name": "toml",
            "dialect": TOMLDialect,
            "encoder": tomli_w.dumps,
        },
        "unpacker": {
            "format_name": "toml",
            "dialect": TOMLDialect,
            "decoder": tomllib.loads,
        },
    }

    @final
    def to_toml(
        self, encoder: Encoder = tomli_w.dumps, **to_dict_kwargs: Any
    ) -> EncodedData: ...

    @classmethod
    @final
    def from_toml(
        cls,
        data: EncodedData,
        decoder: Decoder = tomllib.loads,
        **from_dict_kwargs: Any,
    ) -> Self: ...
