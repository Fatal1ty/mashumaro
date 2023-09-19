from typing import Any, Generic, Optional, Type, TypeVar, Union, final

import tomli_w

from mashumaro.codecs._builder import CodecCodeBuilder
from mashumaro.dialect import Dialect
from mashumaro.mixins.toml import TOMLDialect

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

T = TypeVar("T")
EncodedData = str


class TOMLDecoder(Generic[T]):
    def __init__(
        self,
        shape_type: Union[Type[T], Any],
        *,
        default_dialect: Optional[Type[Dialect]] = None,
    ):
        if default_dialect is not None:
            default_dialect = TOMLDialect.merge(default_dialect)
        else:
            default_dialect = TOMLDialect
        code_builder = CodecCodeBuilder.new(default_dialect=default_dialect)
        code_builder.add_decode_method(shape_type, self, tomllib.loads)

    @final
    def decode(self, data: EncodedData) -> T:
        ...


class TOMLEncoder(Generic[T]):
    def __init__(
        self,
        shape_type: Union[Type[T], Any],
        *,
        default_dialect: Optional[Type[Dialect]] = None,
    ):
        if default_dialect is not None:
            default_dialect = TOMLDialect.merge(default_dialect)
        else:
            default_dialect = TOMLDialect
        code_builder = CodecCodeBuilder.new(default_dialect=default_dialect)
        code_builder.add_encode_method(shape_type, self, tomli_w.dumps)

    @final
    def encode(self, obj: T) -> bytes:
        ...


def decode(data: EncodedData, shape_type: Type[T]) -> T:
    return TOMLDecoder(shape_type).decode(data)


def encode(obj: T, shape_type: Union[Type[T], Any]) -> bytes:
    return TOMLEncoder[T](shape_type).encode(obj)


__all__ = [
    "TOMLDecoder",
    "TOMLEncoder",
    "decode",
    "encode",
]
