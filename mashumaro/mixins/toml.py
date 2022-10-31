from datetime import date, datetime, time
from typing import Any, Callable, Dict, Type, TypeVar

import tomli_w

from mashumaro.dialect import Dialect
from mashumaro.helper import pass_through
from mashumaro.mixins.dict import DataClassDictMixin

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

T = TypeVar("T", bound="DataClassTOMLMixin")


EncodedData = str
Encoder = Callable[[Any], EncodedData]
Decoder = Callable[[EncodedData], Dict[Any, Any]]


class TOMLDialect(Dialect):
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

    def to_toml(
        self: T,
        encoder: Encoder = tomli_w.dumps,
        **to_dict_kwargs,
    ) -> EncodedData:
        ...

    @classmethod
    def from_toml(
        cls: Type[T],
        data: EncodedData,
        decoder: Decoder = tomllib.loads,
        **from_dict_kwargs,
    ) -> T:
        ...
