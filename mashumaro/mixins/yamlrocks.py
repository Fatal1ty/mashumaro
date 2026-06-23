from collections.abc import Callable
from datetime import date, datetime, time
from typing import Any, Type, TypeVar, final
from uuid import UUID

import yamlrocks

from mashumaro.core.helpers import ConfigValue
from mashumaro.dialect import Dialect
from mashumaro.helper import pass_through
from mashumaro.mixins.dict import DataClassDictMixin

T = TypeVar("T", bound="DataClassYAMLRocksMixin")


EncodedData = str | bytes
Encoder = Callable[[Any], bytes]
# yamlrocks.loads is precisely typed and returns a broad union, so the
# decoder alias stays Any rather than narrowing to dict.
Decoder = Callable[[EncodedData], Any]


class YAMLRocksDialect(Dialect):
    no_copy_collections = (list, dict)
    serialization_strategy = {
        datetime: {"serialize": pass_through},
        date: {"serialize": pass_through},
        time: {"serialize": pass_through},
        UUID: {"serialize": pass_through},
    }


class DataClassYAMLRocksMixin(DataClassDictMixin):
    __slots__ = ()

    __mashumaro_builder_params = {
        "packer": {
            "format_name": "yamlb",
            "dialect": YAMLRocksDialect,
            "encoder": yamlrocks.dumps,
            "encoder_kwargs": {
                "option": (
                    "yamlrocks_dumps_options",
                    ConfigValue("yamlrocks_dumps_options"),
                )
            },
        },
        "unpacker": {
            "format_name": "yaml",
            "dialect": YAMLRocksDialect,
            "decoder": yamlrocks.loads,
            "decoder_kwargs": {
                "option": (
                    "yamlrocks_loads_options",
                    ConfigValue("yamlrocks_loads_options"),
                )
            },
        },
    }

    @final
    def to_yamlb(
        self: T,
        encoder: Encoder = yamlrocks.dumps,
        *,
        yamlrocks_dumps_options: int = ...,
        **to_dict_kwargs: Any,
    ) -> bytes: ...

    def to_yaml(self: T, **kwargs: Any) -> str:
        return self.to_yamlb(**kwargs).decode()

    @classmethod
    @final
    def from_yaml(
        cls: Type[T],
        data: EncodedData,
        decoder: Decoder = yamlrocks.loads,
        *,
        yamlrocks_loads_options: int = ...,
        **from_dict_kwargs: Any,
    ) -> T: ...
