from typing import Any, Dict, Type, TypeVar, Union

import yaml
from typing_extensions import Protocol

from mashumaro.mixins.dict import DataClassDictMixin

EncodedData = Union[str, bytes]
T = TypeVar("T", bound="DataClassYAMLMixin")


class Encoder(Protocol):  # pragma no cover
    def __call__(self, o, **kwargs) -> EncodedData:
        ...


class Decoder(Protocol):  # pragma no cover
    def __call__(self, packed: EncodedData, **kwargs) -> Dict[Any, Any]:
        ...


DefaultLoader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
DefaultDumper = getattr(yaml, "CDumper", yaml.Dumper)


def default_encoder(data) -> EncodedData:
    return yaml.dump(data, Dumper=DefaultDumper)


def default_decoder(data: EncodedData) -> Dict[Any, Any]:
    return yaml.load(data, DefaultLoader)


class DataClassYAMLMixin(DataClassDictMixin):
    __slots__ = ()

    def to_yaml(
        self: T,
        encoder: Encoder = default_encoder,  # type: ignore
        **to_dict_kwargs,
    ) -> EncodedData:
        return encoder(self.to_dict(**to_dict_kwargs))

    @classmethod
    def from_yaml(
        cls: Type[T],
        data: EncodedData,
        decoder: Decoder = default_decoder,  # type: ignore
        **from_dict_kwargs,
    ) -> T:
        return cls.from_dict(decoder(data), **from_dict_kwargs)
