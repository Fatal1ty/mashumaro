from collections.abc import Callable
from typing import Any

import yaml
from typing_extensions import Self

from mashumaro.mixins.dict import DataClassDictMixin

EncodedData = str | bytes
Encoder = Callable[[Any], EncodedData]
Decoder = Callable[[EncodedData], dict[Any, Any]]


DefaultLoader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
DefaultDumper = getattr(yaml, "CDumper", yaml.Dumper)


def default_encoder(data: Any) -> EncodedData:
    return yaml.dump(data, Dumper=DefaultDumper)


def default_decoder(data: EncodedData) -> dict[Any, Any]:
    return yaml.load(data, DefaultLoader)


class DataClassYAMLMixin(DataClassDictMixin):
    __slots__ = ()

    def to_yaml(
        self, encoder: Encoder = default_encoder, **to_dict_kwargs: Any
    ) -> EncodedData:
        return encoder(self.to_dict(**to_dict_kwargs))

    @classmethod
    def from_yaml(
        cls,
        data: EncodedData,
        decoder: Decoder = default_decoder,
        **from_dict_kwargs: Any,
    ) -> Self:
        return cls.from_dict(decoder(data), **from_dict_kwargs)
