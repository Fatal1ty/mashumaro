from typing import Any, Callable, Dict, Type, TypeVar

import tomli_w

from mashumaro.mixins.dict import DataClassDictMixin

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

T = TypeVar("T", bound="DataClassTOMLMixin")


EncodedData = str
Encoder = Callable[[Any], EncodedData]
Decoder = Callable[[EncodedData], Dict[Any, Any]]


class DataClassTOMLMixin(DataClassDictMixin):
    __slots__ = ()

    def to_toml(
        self: T,
        encoder: Encoder = tomli_w.dumps,
        **to_dict_kwargs,
    ) -> EncodedData:
        return encoder(self.to_dict(**to_dict_kwargs))

    @classmethod
    def from_toml(
        cls: Type[T],
        data: EncodedData,
        decoder: Decoder = tomllib.loads,
        **from_dict_kwargs,
    ) -> T:
        return cls.from_dict(decoder(data), **from_dict_kwargs)
