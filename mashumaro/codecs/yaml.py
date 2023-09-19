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

import yaml

from mashumaro.codecs._builder import CodecCodeBuilder
from mashumaro.dialect import Dialect

T = TypeVar("T")


EncodedData = Union[str, bytes]
PostEncoderFunc = Callable[[Any], EncodedData]
PreDecoderFunc = Callable[[EncodedData], Any]


DefaultLoader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
DefaultDumper = getattr(yaml, "CDumper", yaml.Dumper)


def _default_encoder(data: Any) -> EncodedData:
    return yaml.dump(data, Dumper=DefaultDumper)


def _default_decoder(data: EncodedData) -> Any:
    return yaml.load(data, DefaultLoader)


class YAMLDecoder(Generic[T]):
    def __init__(
        self,
        shape_type: Union[Type[T], Any],
        *,
        default_dialect: Optional[Type[Dialect]] = None,
        pre_decoder_func: Optional[PreDecoderFunc] = _default_decoder,
    ):
        code_builder = CodecCodeBuilder.new(default_dialect=default_dialect)
        code_builder.add_decode_method(shape_type, self, pre_decoder_func)

    @final
    def decode(self, data: EncodedData) -> T:
        ...


class YAMLEncoder(Generic[T]):
    def __init__(
        self,
        shape_type: Union[Type[T], Any],
        *,
        default_dialect: Optional[Type[Dialect]] = None,
        post_encoder_func: Optional[PostEncoderFunc] = _default_encoder,
    ):
        code_builder = CodecCodeBuilder.new(default_dialect=default_dialect)
        code_builder.add_encode_method(shape_type, self, post_encoder_func)

    @final
    def encode(self, obj: T) -> EncodedData:
        ...


def decode(data: EncodedData, shape_type: Union[Type[T], Any]) -> T:
    return YAMLDecoder(shape_type).decode(data)


def encode(obj: T, shape_type: Union[Type[T], Any]) -> EncodedData:
    return YAMLEncoder[T](shape_type).encode(obj)


__all__ = [
    "YAMLDecoder",
    "YAMLEncoder",
    "decode",
    "encode",
]
