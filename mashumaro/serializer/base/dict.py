from typing import Any, Dict, Mapping, Type, TypeVar

from mashumaro.exceptions import UnresolvedTypeReferenceError
from mashumaro.serializer.base.metaprogramming import CodeBuilder

T = TypeVar("T", bound="DataClassDictMixin")


class DataClassDictMixin:
    __slots__ = ()

    def __init_subclass__(cls: Type[T], **kwargs):
        builder = CodeBuilder(cls)
        config = builder.get_config()
        try:
            builder.add_from_dict()
        except UnresolvedTypeReferenceError:
            if not config.allow_postponed_evaluation:
                raise
        try:
            builder.add_to_dict()
        except UnresolvedTypeReferenceError:
            if not config.allow_postponed_evaluation:
                raise

    def to_dict(
        self: T,
        use_bytes: bool = False,
        use_enum: bool = False,
        use_datetime: bool = False,
        # *
        # keyword-only flags that are exist with the code generation options:
        # omit_none: bool = False
        # by_alias: bool = False
        **kwargs,
    ) -> dict:
        builder = CodeBuilder(self.__class__)
        builder.add_to_dict()
        return self.to_dict(use_bytes, use_enum, use_datetime, **kwargs)

    @classmethod
    def from_dict(
        cls: Type[T],
        d: Mapping,
        use_bytes: bool = False,
        use_enum: bool = False,
        use_datetime: bool = False,
    ) -> T:
        builder = CodeBuilder(cls)
        builder.add_from_dict()
        return cls.from_dict(d, use_bytes, use_enum, use_datetime)

    @classmethod
    def __pre_deserialize__(cls: Type[T], d: Dict[Any, Any]) -> Dict[Any, Any]:
        ...

    @classmethod
    def __post_deserialize__(cls: Type[T], obj: T) -> T:
        ...

    def __pre_serialize__(self: T) -> T:
        ...

    def __post_serialize__(self: T, d: Dict[Any, Any]) -> Dict[Any, Any]:
        ...


__all__ = ["DataClassDictMixin"]
