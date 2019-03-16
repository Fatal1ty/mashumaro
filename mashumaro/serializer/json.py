import json
from typing import Union, Optional, Callable, Dict, Mapping, TypeVar, Type
from types import MappingProxyType

from mashumaro.serializer.base import DataClassDictMixin


DEFAULT_DICT_PARAMS = {
    'use_bytes': False,
    'use_enum': False,
    'use_datetime': False
}
EncodedData = Union[str, bytes, bytearray]
Encoder = Callable[[Dict], EncodedData]
Decoder = Callable[[EncodedData], Dict]
T = TypeVar('T', bound='DataClassJSONMixin')


class DataClassJSONMixin(DataClassDictMixin):
    def to_json(
            self: T,
            encoder: Optional[Encoder] = json.dumps,
            dict_params: Optional[Mapping] = MappingProxyType({}),
            **encoder_kwargs) -> EncodedData:

        return encoder(
            self.to_dict(**dict(DEFAULT_DICT_PARAMS, **dict_params)),
            **encoder_kwargs
        )

    @classmethod
    def from_json(
            cls: Type[T],
            data: EncodedData,
            decoder: Optional[Decoder] = json.loads,
            dict_params: Optional[Mapping] = MappingProxyType({}),
            **decoder_kwargs) -> T:

        return cls.from_dict(
            decoder(data, **decoder_kwargs),
            **dict(DEFAULT_DICT_PARAMS, **dict_params)
        )
