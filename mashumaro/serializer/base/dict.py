from typing import Mapping, Callable, Type, Any, Optional

from mashumaro.serializer.base.metaprogramming import CodeBuilder

EncodeHook = Callable[[Any, dict], dict]
DecodeHook = Callable[[Type[Any], dict], dict]

class DataClassDictMixin:
    def __init_subclass__(cls, **kwargs):
        builder = CodeBuilder(cls)
        exc = None
        try:
            builder.add_from_dict()
        except Exception as e:
            exc = e
        try:
            builder.add_to_dict()
        except Exception as e:
            exc = e
        if exc:
            raise exc

    def to_dict(
            self,
            use_bytes: bool = False,
            use_enum: bool = False,
            use_datetime: bool = False,
            encode_hook: Optional[EncodeHook] = None) -> dict:
        pass

    @classmethod
    def from_dict(
            cls,
            d: Mapping,
            use_bytes: bool = False,
            use_enum: bool = False,
            use_datetime: bool = False,
            decode_hook: Optional[DecodeHook] = None) -> 'DataClassDictMixin':
        pass


__all__ = [DataClassDictMixin]
