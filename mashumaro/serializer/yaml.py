from typing import Union, Optional, Callable, Dict, Mapping, TypeVar, Type
from types import MappingProxyType

import yaml

from mashumaro.serializer.base import DataClassDictMixin


DEFAULT_DICT_PARAMS = {
    'use_bytes': False,
    'use_enum': False,
    'use_datetime': False
}
EncodedData = Union[str, bytes]
Encoder = Callable[[Dict], EncodedData]
Decoder = Callable[[EncodedData], Dict]
T = TypeVar('T', bound='DataClassYAMLMixin')


class DataClassYAMLMixin(DataClassDictMixin):
    def to_yaml(
            self: T,
            encoder: Optional[Encoder] = yaml.dump,
            dict_params: Optional[Mapping] = MappingProxyType({}),
            **encoder_kwargs) -> EncodedData:

        return encoder(
            self.to_dict(**dict(DEFAULT_DICT_PARAMS, **dict_params)),
            **encoder_kwargs
        )

    @classmethod
    def from_yaml(
            cls: Type[T],
            data: EncodedData,
            decoder: Optional[Decoder] = yaml.safe_load,
            dict_params: Optional[Mapping] = MappingProxyType({}),
            **decoder_kwargs) -> T:
        return cls.from_dict(
            decoder(data, **decoder_kwargs),
            **dict(DEFAULT_DICT_PARAMS, **dict_params)
        )
