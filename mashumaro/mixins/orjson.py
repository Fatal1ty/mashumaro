from datetime import date, datetime, time
from typing import Any, Callable, Dict, Type, TypeVar, Union
from uuid import UUID

import orjson

from mashumaro.core.meta.mixin import (
    compile_mixin_packer,
    compile_mixin_unpacker,
)
from mashumaro.dialect import Dialect
from mashumaro.helper import pass_through
from mashumaro.mixins.dict import DataClassDictMixin

T = TypeVar("T", bound="DataClassJSONMixin")


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

    def to_jsonb(
        self: T,
        encoder: Encoder = orjson.dumps,
        **to_dict_kwargs,
    ) -> bytes:
        compile_mixin_packer(self, "jsonb", OrjsonDialect, encoder)
        return self.to_jsonb(encoder, **to_dict_kwargs)

    def to_json(
        self: T,
        encoder: Encoder = orjson.dumps,
        **to_dict_kwargs,
    ) -> str:
        return self.to_jsonb(encoder, **to_dict_kwargs).decode()

    @classmethod
    def from_json(
        cls: Type[T],
        data: EncodedData,
        decoder: Decoder = orjson.loads,
        **from_dict_kwargs,
    ) -> T:
        compile_mixin_unpacker(cls, "json", OrjsonDialect, decoder)
        return cls.from_json(data, decoder, **from_dict_kwargs)
