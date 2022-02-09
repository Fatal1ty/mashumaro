from typing import Any, Dict, Mapping, Type, TypeVar

from mashumaro.core.meta.builder import CodeBuilder
from mashumaro.exceptions import UnresolvedTypeReferenceError

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
        # *
        # keyword-only arguments that exist with the code generation options:
        # omit_none: bool = False
        # by_alias: bool = False
        # dialect: Type[Dialect] = None
        **kwargs,
    ) -> dict:
        ...

    @classmethod
    def from_dict(
        cls: Type[T],
        d: Mapping,
        # *
        # keyword-only arguments that exist with the code generation options:
        # dialect: Type[Dialect] = None
        **kwargs,
    ) -> T:
        ...

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
