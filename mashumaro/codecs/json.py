import json
from typing import (
    Any,
    Callable,
    Generic,
    Optional,
    Type,
    TypeVar,
    Union,
    final,
)

from mashumaro.codecs._builder import CodecCodeBuilder
from mashumaro.dialect import Dialect

T = TypeVar("T")
EncodedData = Union[str, bytes, bytearray]


class JSONDecoder(Generic[T]):
    def __init__(
        self,
        shape_type: Union[Type[T], Any],
        *,
        default_dialect: Optional[Type[Dialect]] = None,
        pre_decoder_func: Callable[[EncodedData], Any] = json.loads,
    ):
        code_builder = CodecCodeBuilder.new(default_dialect=default_dialect)
        code_builder.add_decode_method(shape_type, self, pre_decoder_func)

    @final
    def decode(self, data: EncodedData) -> T:
        ...


class JSONEncoder(Generic[T]):
    def __init__(
        self,
        shape_type: Union[Type[T], Any],
        *,
        default_dialect: Optional[Type[Dialect]] = None,
        post_encoder_func: Callable[[Any], str] = json.dumps,
    ):
        code_builder = CodecCodeBuilder.new(default_dialect=default_dialect)
        code_builder.add_encode_method(shape_type, self, post_encoder_func)

    @final
    def encode(self, obj: T) -> str:
        ...


def decode(
    data: EncodedData,
    shape_type: Union[Type[T], Any],
    pre_decoder_func: Callable[[EncodedData], Any] = json.loads,
) -> T:
    return JSONDecoder(shape_type, pre_decoder_func=pre_decoder_func).decode(
        data
    )


def encode(
    obj: T,
    shape_type: Union[Type[T], Any],
    post_encoder_func: Callable[[Any], str] = json.dumps,
) -> str:
    return JSONEncoder[T](
        shape_type, post_encoder_func=post_encoder_func
    ).encode(obj)


__all__ = [
    "JSONDecoder",
    "JSONEncoder",
    "decode",
    "encode",
]
