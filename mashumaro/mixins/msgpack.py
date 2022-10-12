from typing import Any, Callable, Dict, Type, TypeVar

import msgpack

from mashumaro.core.meta.mixin import (
    compile_mixin_packer,
    compile_mixin_unpacker,
)
from mashumaro.dialect import Dialect
from mashumaro.helper import pass_through
from mashumaro.mixins.dict import DataClassDictMixin

T = TypeVar("T", bound="DataClassMessagePackMixin")


EncodedData = bytes
Encoder = Callable[[Any], EncodedData]
Decoder = Callable[[EncodedData], Dict[Any, Any]]


class MessagePackDialect(Dialect):
    serialization_strategy = {
        bytes: pass_through,  # type: ignore
        bytearray: {
            "deserialize": bytearray,
            "serialize": pass_through,
        },
    }


def default_encoder(data) -> EncodedData:
    return msgpack.packb(data, use_bin_type=True)


def default_decoder(data: EncodedData) -> Dict[Any, Any]:
    return msgpack.unpackb(data, raw=False)


class DataClassMessagePackMixin(DataClassDictMixin):
    __slots__ = ()

    def to_msgpack(
        self: T,
        encoder: Encoder = default_encoder,
        **to_dict_kwargs,
    ) -> EncodedData:
        compile_mixin_packer(self, "msgpack", MessagePackDialect, encoder)
        return self.to_msgpack(encoder, **to_dict_kwargs)

    @classmethod
    def from_msgpack(
        cls: Type[T],
        data: EncodedData,
        decoder: Decoder = default_decoder,
        **from_dict_kwargs,
    ) -> T:
        compile_mixin_unpacker(cls, "msgpack", MessagePackDialect, decoder)
        return cls.from_msgpack(data, decoder, **from_dict_kwargs)
