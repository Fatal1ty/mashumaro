from collections.abc import Callable
from typing import Any, Generic, TypeVar, final

from typing_extensions import TypeForm

from mashumaro.codecs._builder import CodecCodeBuilder
from mashumaro.core.meta.helpers import get_args
from mashumaro.dialect import Dialect

T = TypeVar("T")


class BasicDecoder(Generic[T]):
    def __init__(
        self,
        shape_type: TypeForm[T],
        *,
        default_dialect: type[Dialect] | None = None,
        pre_decoder_func: Callable[[Any], Any] | None = None,
    ):
        code_builder = CodecCodeBuilder.new(
            type_args=get_args(shape_type), default_dialect=default_dialect
        )
        code_builder.add_decode_method(shape_type, self, pre_decoder_func)

    @final
    def decode(self, data: Any) -> T: ...


class BasicEncoder(Generic[T]):
    def __init__(
        self,
        shape_type: TypeForm[T],
        *,
        default_dialect: type[Dialect] | None = None,
        post_encoder_func: Callable[[Any], Any] | None = None,
    ):
        code_builder = CodecCodeBuilder.new(
            type_args=get_args(shape_type), default_dialect=default_dialect
        )
        code_builder.add_encode_method(shape_type, self, post_encoder_func)

    @final
    def encode(self, obj: T) -> Any: ...


def decode(data: Any, shape_type: TypeForm[T]) -> T:
    return BasicDecoder(shape_type).decode(data)


def encode(obj: T, shape_type: TypeForm[T]) -> Any:
    return BasicEncoder(shape_type).encode(obj)


__all__ = ["BasicDecoder", "BasicEncoder", "decode", "encode"]
