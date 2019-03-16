from typing import Union, Optional, Callable, Dict, Mapping, TypeVar, Type
from types import MappingProxyType
from functools import partial

import msgpack

from mashumaro.serializer.base import DataClassDictMixin


DEFAULT_DICT_PARAMS = {
    'use_bytes': True,
    'use_enum': False,
    'use_datetime': False
}
EncodedData = Union[str, bytes, bytearray]
Encoder = Callable[[Dict], EncodedData]
Decoder = Callable[[EncodedData], Dict]
T = TypeVar('T', bound='DataClassMessagePackMixin')


class DataClassMessagePackMixin(DataClassDictMixin):
    def to_msgpack(
            self: T,
            encoder: Optional[Encoder] = partial(
                msgpack.packb, use_bin_type = True
            ),
            dict_params: Optional[Mapping] = MappingProxyType({}),
            **encoder_kwargs) -> EncodedData:

        return encoder(
            self.to_dict(**dict(DEFAULT_DICT_PARAMS, **dict_params)),
            **encoder_kwargs
        )

    @classmethod
    def from_msgpack(
            cls: Type[T],
            data: EncodedData,
            decoder: Optional[Decoder] = partial(msgpack.unpackb, raw = False),
            dict_params: Optional[Mapping] = MappingProxyType({}),
            **decoder_kwargs) -> T:
        return cls.from_dict(
            decoder(data, **decoder_kwargs),
            **dict(DEFAULT_DICT_PARAMS, **dict_params)
        )
