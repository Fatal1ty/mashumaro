import json
from collections.abc import Callable
from typing import Any

from typing_extensions import Self

from mashumaro.mixins.dict import DataClassDictMixin

EncodedData = str | bytes | bytearray
Encoder = Callable[[Any], EncodedData]
Decoder = Callable[[EncodedData], dict[Any, Any]]


class DataClassJSONMixin(DataClassDictMixin):
    __slots__ = ()

    def to_json(
        self, encoder: Encoder = json.dumps, **to_dict_kwargs: Any
    ) -> EncodedData:
        return encoder(self.to_dict(**to_dict_kwargs))

    @classmethod
    def from_json(
        cls,
        data: EncodedData,
        decoder: Decoder = json.loads,
        **from_dict_kwargs: Any,
    ) -> Self:
        return cls.from_dict(decoder(data), **from_dict_kwargs)
