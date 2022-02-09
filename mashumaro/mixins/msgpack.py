from functools import partial
from typing import Any, Dict, Type, TypeVar

import msgpack
from typing_extensions import Protocol

from mashumaro.dialects.msgpack import MessagePackDialect
from mashumaro.mixins.dict import DataClassDictMixin

EncodedData = bytes
T = TypeVar("T", bound="DataClassMessagePackMixin")

DEFAULT_DICT_PARAMS = {"dialect": MessagePackDialect}


class Encoder(Protocol):  # pragma no cover
    def __call__(self, o, **kwargs) -> EncodedData:
        ...


class Decoder(Protocol):  # pragma no cover
    def __call__(self, packed: EncodedData, **kwargs) -> Dict[Any, Any]:
        ...


class DataClassMessagePackMixin(DataClassDictMixin):
    __slots__ = ()

    def to_msgpack(
        self: T,
        encoder: Encoder = partial(msgpack.packb, use_bin_type=True),
        **to_dict_kwargs,
    ) -> EncodedData:

        return encoder(
            self.to_dict(**dict(DEFAULT_DICT_PARAMS, **to_dict_kwargs))
        )

    @classmethod
    def from_msgpack(
        cls: Type[T],
        data: EncodedData,
        decoder: Decoder = partial(msgpack.unpackb, raw=False),
        **from_dict_kwargs,
    ) -> T:
        return cls.from_dict(
            decoder(data),
            **dict(DEFAULT_DICT_PARAMS, **from_dict_kwargs),
        )
