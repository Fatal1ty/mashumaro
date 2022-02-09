import json
from typing import Any, Dict, Type, TypeVar, Union

from typing_extensions import Protocol

from mashumaro.mixins.dict import DataClassDictMixin

EncodedData = Union[str, bytes, bytearray]
T = TypeVar("T", bound="DataClassJSONMixin")


class Encoder(Protocol):  # pragma no cover
    def __call__(self, obj, **kwargs) -> EncodedData:
        ...


class Decoder(Protocol):  # pragma no cover
    def __call__(self, s: EncodedData, **kwargs) -> Dict[Any, Any]:
        ...


class DataClassJSONMixin(DataClassDictMixin):
    __slots__ = ()

    def to_json(
        self: T,
        encoder: Encoder = json.dumps,
        **to_dict_kwargs,
    ) -> EncodedData:
        return encoder(self.to_dict(**to_dict_kwargs))

    @classmethod
    def from_json(
        cls: Type[T],
        data: EncodedData,
        decoder: Decoder = json.loads,
        **from_dict_kwargs,
    ) -> T:
        return cls.from_dict(decoder(data), **from_dict_kwargs)
