from collections.abc import Callable
from typing import Any, Generic, Type, TypeVar, final, overload

import yamlrocks

from mashumaro.codecs._builder import CodecCodeBuilder
from mashumaro.core.meta.helpers import get_args
from mashumaro.dialect import Dialect
from mashumaro.mixins.yamlrocks import YAMLRocksDialect

T = TypeVar("T")


EncodedData = str | bytes
PreDecoderFunc = Callable[[EncodedData], Any]
PostEncoderFunc = Callable[[Any], bytes]


class YAMLRocksDecoder(Generic[T]):
    @overload
    def __init__(
        self,
        shape_type: Type[T],
        *,
        default_dialect: Type[Dialect] | None = None,
        pre_decoder_func: PreDecoderFunc = yamlrocks.loads,
    ): ...

    @overload
    def __init__(
        self,
        shape_type: Any,
        *,
        default_dialect: Type[Dialect] | None = None,
        pre_decoder_func: PreDecoderFunc = yamlrocks.loads,
    ): ...

    def __init__(
        self,
        shape_type: Type[T] | Any,
        *,
        default_dialect: Type[Dialect] | None = None,
        pre_decoder_func: PreDecoderFunc = yamlrocks.loads,
    ):
        if default_dialect is not None:
            default_dialect = YAMLRocksDialect.merge(default_dialect)
        else:
            default_dialect = YAMLRocksDialect
        code_builder = CodecCodeBuilder.new(
            type_args=get_args(shape_type), default_dialect=default_dialect
        )
        code_builder.add_decode_method(shape_type, self, pre_decoder_func)

    @final
    def decode(self, data: EncodedData) -> T: ...


class YAMLRocksEncoder(Generic[T]):
    @overload
    def __init__(
        self,
        shape_type: Type[T],
        *,
        default_dialect: Type[Dialect] | None = None,
        post_encoder_func: PostEncoderFunc = yamlrocks.dumps,
    ): ...

    @overload
    def __init__(
        self,
        shape_type: Any,
        *,
        default_dialect: Type[Dialect] | None = None,
        post_encoder_func: PostEncoderFunc = yamlrocks.dumps,
    ): ...

    def __init__(
        self,
        shape_type: Type[T] | Any,
        *,
        default_dialect: Type[Dialect] | None = None,
        post_encoder_func: PostEncoderFunc = yamlrocks.dumps,
    ):
        if default_dialect is not None:
            default_dialect = YAMLRocksDialect.merge(default_dialect)
        else:
            default_dialect = YAMLRocksDialect
        code_builder = CodecCodeBuilder.new(
            type_args=get_args(shape_type), default_dialect=default_dialect
        )
        code_builder.add_encode_method(shape_type, self, post_encoder_func)

    @final
    def encode(self, obj: T) -> bytes: ...


def yaml_decode(data: EncodedData, shape_type: Type[T]) -> T:
    return YAMLRocksDecoder(shape_type).decode(data)


def yaml_encode(obj: T, shape_type: Type[T] | Any) -> bytes:
    return YAMLRocksEncoder(shape_type).encode(obj)


decode = yaml_decode
encode = yaml_encode


__all__ = [
    "YAMLRocksDecoder",
    "YAMLRocksEncoder",
    "yaml_decode",
    "yaml_encode",
    "decode",
    "encode",
]
