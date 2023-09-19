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

import msgpack

from mashumaro.codecs._builder import CodecCodeBuilder
from mashumaro.dialect import Dialect
from mashumaro.mixins.msgpack import MessagePackDialect

T = TypeVar("T")


EncodedData = bytes
PostEncoderFunc = Callable[[Any], EncodedData]
PreDecoderFunc = Callable[[EncodedData], Any]


def _default_decoder(data: EncodedData) -> Any:
    return msgpack.unpackb(data, raw=False)


def _default_encoder(data: Any) -> EncodedData:
    return msgpack.packb(data, use_bin_type=True)


class MessagePackDecoder(Generic[T]):
    def __init__(
        self,
        shape_type: Union[Type[T], Any],
        *,
        default_dialect: Optional[Type[Dialect]] = None,
        pre_decoder_func: Optional[PreDecoderFunc] = _default_decoder,
    ):
        if default_dialect is not None:
            default_dialect = MessagePackDialect.merge(default_dialect)
        else:
            default_dialect = MessagePackDialect
        code_builder = CodecCodeBuilder.new(default_dialect=default_dialect)
        code_builder.add_decode_method(shape_type, self, pre_decoder_func)

    @final
    def decode(self, data: EncodedData) -> T:
        ...


class MessagePackEncoder(Generic[T]):
    def __init__(
        self,
        shape_type: Union[Type[T], Any],
        *,
        default_dialect: Optional[Type[Dialect]] = None,
        post_encoder_func: Optional[PostEncoderFunc] = _default_encoder,
    ):
        if default_dialect is not None:
            default_dialect = MessagePackDialect.merge(default_dialect)
        else:
            default_dialect = MessagePackDialect
        code_builder = CodecCodeBuilder.new(default_dialect=default_dialect)
        code_builder.add_encode_method(shape_type, self, post_encoder_func)

    @final
    def encode(self, obj: T) -> EncodedData:
        ...


def decode(data: EncodedData, shape_type: Union[Type[T], Any]) -> T:
    return MessagePackDecoder(shape_type).decode(data)


def encode(obj: T, shape_type: Union[Type[T], Any]) -> EncodedData:
    return MessagePackEncoder[T](shape_type).encode(obj)


__all__ = [
    "MessagePackDecoder",
    "MessagePackEncoder",
    "decode",
    "encode",
]
