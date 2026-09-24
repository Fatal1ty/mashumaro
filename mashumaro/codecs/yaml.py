from collections.abc import Callable
from typing import Any, Generic, TypeVar, final

import yaml
from typing_extensions import TypeForm

from mashumaro.codecs._builder import CodecCodeBuilder
from mashumaro.core.meta.helpers import get_args
from mashumaro.dialect import Dialect

T = TypeVar("T")


EncodedData = str | bytes
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
        shape_type: TypeForm[T],
        *,
        default_dialect: type[Dialect] | None = None,
        pre_decoder_func: PreDecoderFunc | None = _default_decoder,
    ):
        code_builder = CodecCodeBuilder.new(
            type_args=get_args(shape_type), default_dialect=default_dialect
        )
        code_builder.add_decode_method(shape_type, self, pre_decoder_func)

    @final
    def decode(self, data: EncodedData) -> T: ...


class YAMLEncoder(Generic[T]):
    def __init__(
        self,
        shape_type: TypeForm[T],
        *,
        default_dialect: type[Dialect] | None = None,
        post_encoder_func: PostEncoderFunc | None = _default_encoder,
    ):
        code_builder = CodecCodeBuilder.new(
            type_args=get_args(shape_type), default_dialect=default_dialect
        )
        code_builder.add_encode_method(shape_type, self, post_encoder_func)

    @final
    def encode(self, obj: T) -> EncodedData: ...


def yaml_decode(data: EncodedData, shape_type: TypeForm[T]) -> T:
    return YAMLDecoder(shape_type).decode(data)


def yaml_encode(obj: T, shape_type: TypeForm[T]) -> EncodedData:
    return YAMLEncoder(shape_type).encode(obj)


decode = yaml_decode
encode = yaml_encode


__all__ = [
    "YAMLDecoder",
    "YAMLEncoder",
    "decode",
    "encode",
    "yaml_decode",
    "yaml_encode",
]
