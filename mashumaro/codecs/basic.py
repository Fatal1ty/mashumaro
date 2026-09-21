from collections.abc import Callable
from typing import Any, Generic, TypeVar, final, overload

from mashumaro.codecs._builder import CodecCodeBuilder
from mashumaro.core.meta.helpers import get_args
from mashumaro.dialect import Dialect

T = TypeVar("T")


class BasicDecoder(Generic[T]):
    @overload
    def __init__(
        self,
        shape_type: type[T],
        *,
        default_dialect: type[Dialect] | None = None,
        pre_decoder_func: Callable[[Any], Any] | None = None,
    ): ...

    @overload
    def __init__(
        self,
        shape_type: Any,
        *,
        default_dialect: type[Dialect] | None = None,
        pre_decoder_func: Callable[[Any], Any] | None = None,
    ): ...

    def __init__(
        self,
        shape_type: type[T] | Any,
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
    @overload
    def __init__(
        self,
        shape_type: type[T],
        *,
        default_dialect: type[Dialect] | None = None,
        post_encoder_func: Callable[[Any], Any] | None = None,
    ): ...

    @overload
    def __init__(
        self,
        shape_type: Any,
        *,
        default_dialect: type[Dialect] | None = None,
        post_encoder_func: Callable[[Any], Any] | None = None,
    ): ...

    def __init__(
        self,
        shape_type: type[T] | Any,
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


def decode(data: Any, shape_type: type[T] | Any) -> T:
    return BasicDecoder(shape_type).decode(data)


def encode(obj: T, shape_type: type[T] | Any) -> Any:
    return BasicEncoder(shape_type).encode(obj)


__all__ = ["BasicDecoder", "BasicEncoder", "decode", "encode"]
