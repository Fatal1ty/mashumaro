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


class DataClassYAMLMixin(DataClassDictMixin):
    __slots__ = ()

    def to_yaml(
        self: T,
        encoder: Encoder = yaml.dump,  # type: ignore
        **to_dict_kwargs,
    ) -> EncodedData:
        return encoder(self.to_dict(**to_dict_kwargs))

    @classmethod
    def from_yaml(
        cls: Type[T],
        data: EncodedData,
        decoder: Decoder = yaml.safe_load,  # type: ignore
        **from_dict_kwargs,
    ) -> T:
        return cls.from_dict(decoder(data), **from_dict_kwargs)
