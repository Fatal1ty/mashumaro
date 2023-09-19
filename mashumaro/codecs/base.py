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


class Decoder(Generic[T]):
    def __init__(
        self,
        shape_type: Union[Type[T], Any],
        *,
        default_dialect: Optional[Type[Dialect]] = None,
        pre_decoder_func: Optional[Callable[[Any], Any]] = None,
    ):
        code_builder = CodecCodeBuilder.new(default_dialect=default_dialect)
        code_builder.add_decode_method(shape_type, self, pre_decoder_func)

    @final
    def decode(self, data: Any) -> T:
        ...


class Encoder(Generic[T]):
    def __init__(
        self,
        shape_type: Union[Type[T], Any],
        *,
        default_dialect: Optional[Type[Dialect]] = None,
        post_encoder_func: Optional[Callable[[Any], Any]] = None,
    ):
        code_builder = CodecCodeBuilder.new(default_dialect=default_dialect)
        code_builder.add_encode_method(shape_type, self, post_encoder_func)

    @final
    def encode(self, obj: T) -> Any:
        ...


def decode(data: Any, shape_type: Union[Type[T], Any]) -> T:
    return Decoder(shape_type).decode(data)


def encode(obj: T, shape_type: Union[Type[T], Any]) -> Any:
    return Encoder[T](shape_type).encode(obj)


__all__ = [
    "Decoder",
    "Encoder",
    "decode",
    "encode",
]
