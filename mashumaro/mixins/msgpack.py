from typing import Any, Callable, Dict, Type, TypeVar

import msgpack

from mashumaro.dialects.msgpack import MessagePackDialect
from mashumaro.mixins.dict import DataClassDictMixin

T = TypeVar("T", bound="DataClassMessagePackMixin")

DEFAULT_DICT_PARAMS = {"dialect": MessagePackDialect}


EncodedData = bytes
Encoder = Callable[[Any], EncodedData]
Decoder = Callable[[EncodedData], Dict[Any, Any]]


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

        return encoder(
            self.to_dict(**dict(DEFAULT_DICT_PARAMS, **to_dict_kwargs))
        )

    @classmethod
    def from_msgpack(
        cls: Type[T],
        data: EncodedData,
        decoder: Decoder = default_decoder,
        **from_dict_kwargs,
    ) -> T:
        return cls.from_dict(
            decoder(data),
            **dict(DEFAULT_DICT_PARAMS, **from_dict_kwargs),
        )
