from typing import Generic, TypeVar, final

import orjson
from typing_extensions import TypeForm

from mashumaro.codecs._builder import CodecCodeBuilder
from mashumaro.core.meta.helpers import get_args
from mashumaro.dialect import Dialect
from mashumaro.mixins.orjson import OrjsonDialect

T = TypeVar("T")
EncodedData = str | bytes | bytearray


class ORJSONDecoder(Generic[T]):
    def __init__(
        self,
        shape_type: TypeForm[T],
        *,
        default_dialect: type[Dialect] | None = None,
    ):
        if default_dialect is not None:
            default_dialect = OrjsonDialect.merge(default_dialect)
        else:
            default_dialect = OrjsonDialect
        code_builder = CodecCodeBuilder.new(
            type_args=get_args(shape_type), default_dialect=default_dialect
        )
        code_builder.add_decode_method(shape_type, self, orjson.loads)

    @final
    def decode(self, data: EncodedData) -> T: ...


class ORJSONEncoder(Generic[T]):
    def __init__(
        self,
        shape_type: TypeForm[T],
        *,
        default_dialect: type[Dialect] | None = None,
    ):
        if default_dialect is not None:
            default_dialect = OrjsonDialect.merge(default_dialect)
        else:
            default_dialect = OrjsonDialect
        code_builder = CodecCodeBuilder.new(
            type_args=get_args(shape_type), default_dialect=default_dialect
        )
        code_builder.add_encode_method(shape_type, self, orjson.dumps)

    @final
    def encode(self, obj: T) -> bytes: ...


def json_decode(data: EncodedData, shape_type: TypeForm[T]) -> T:
    return ORJSONDecoder(shape_type).decode(data)


def json_encode(obj: T, shape_type: TypeForm[T]) -> bytes:
    return ORJSONEncoder(shape_type).encode(obj)


decode = json_decode
encode = json_encode


__all__ = [
    "ORJSONDecoder",
    "ORJSONEncoder",
    "decode",
    "encode",
    "json_decode",
    "json_encode",
]
