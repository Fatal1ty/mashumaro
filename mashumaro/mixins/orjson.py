from datetime import date, datetime, time
from typing import Any, Callable, Dict, Type, TypeVar, Union
from uuid import UUID

import orjson

from mashumaro.core.helpers import ConfigValue
from mashumaro.dialect import Dialect
from mashumaro.helper import pass_through
from mashumaro.mixins.dict import DataClassDictMixin

T = TypeVar("T", bound="DataClassORJSONMixin")


EncodedData = Union[str, bytes, bytearray]
Encoder = Callable[[Any], EncodedData]
Decoder = Callable[[EncodedData], Dict[Any, Any]]


class OrjsonDialect(Dialect):
    serialization_strategy = {
        datetime: {"serialize": pass_through},
        date: {"serialize": pass_through},
        time: {"serialize": pass_through},
        UUID: {"serialize": pass_through},
    }


class DataClassORJSONMixin(DataClassDictMixin):
    __slots__ = ()

    __mashumaro_builder_params = {
        "packer": {
            "format_name": "jsonb",
            "dialect": OrjsonDialect,
            "encoder": orjson.dumps,
            "encoder_kwargs": {
                "option": ("orjson_options", ConfigValue("orjson_options")),
            },
        },
        "unpacker": {
            "format_name": "json",
            "dialect": OrjsonDialect,
            "decoder": orjson.loads,
        },
    }

    def to_jsonb(
        self: T,
        encoder: Encoder = orjson.dumps,
        *,
        orjson_options: int = ...,
        **to_dict_kwargs: Any,
    ) -> bytes:
        ...

    def to_json(self: T, **kwargs: Any) -> str:
        return self.to_jsonb(**kwargs).decode()

    @classmethod
    def from_json(
        cls: Type[T],
        data: EncodedData,
        decoder: Decoder = orjson.loads,
        **from_dict_kwargs: Any,
    ) -> T:
        ...
