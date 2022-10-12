from datetime import date, datetime, time
from typing import Any, Callable, Dict, Type, TypeVar

import tomli_w

from mashumaro.core.meta.mixin import (
    compile_mixin_packer,
    compile_mixin_unpacker,
)
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
    serialization_strategy = {
        datetime: pass_through,
        date: pass_through,
        time: pass_through,
    }


class DataClassTOMLMixin(DataClassDictMixin):
    __slots__ = ()

    def to_toml(
        self: T,
        encoder: Encoder = tomli_w.dumps,
        **to_dict_kwargs,
    ) -> EncodedData:
        compile_mixin_packer(self, "toml", TOMLDialect, encoder)
        return self.to_toml(encoder, **to_dict_kwargs)

    @classmethod
    def from_toml(
        cls: Type[T],
        data: EncodedData,
        decoder: Decoder = tomllib.loads,
        **from_dict_kwargs,
    ) -> T:
        compile_mixin_unpacker(cls, "toml", TOMLDialect, decoder)
        return cls.from_toml(data, decoder, **from_dict_kwargs)
