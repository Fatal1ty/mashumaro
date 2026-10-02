from collections.abc import Callable
from typing import Any, TypeAlias, final

import orjson
from typing_extensions import Self

from mashumaro.dialect import Dialect
from mashumaro.mixins.dict import DataClassDictMixin

EncodedData: TypeAlias = str | bytes | bytearray
Encoder: TypeAlias = Callable[[Any], EncodedData]
Decoder: TypeAlias = Callable[[EncodedData], dict[Any, Any]]

class OrjsonDialect(Dialect):
    serialization_strategy: Any

class DataClassORJSONMixin(DataClassDictMixin):
    __slots__ = ()
    @final
    def to_jsonb(
        self,
        encoder: Encoder = orjson.dumps,
        *,
        orjson_options: int = ...,
        **to_dict_kwargs: Any,
    ) -> bytes: ...
    def to_json(
        self,
        encoder: Encoder = orjson.dumps,
        *,
        orjson_options: int = ...,
        **to_dict_kwargs: Any,
    ) -> str: ...
    @classmethod
    @final
    def from_json(
        cls,
        data: EncodedData,
        decoder: Decoder = orjson.loads,
        **from_dict_kwargs: Any,
    ) -> Self: ...
