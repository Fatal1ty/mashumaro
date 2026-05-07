from typing import Any, Type

from mashumaro.core.meta.code.builder import CodeBuilder
from mashumaro.dialect import Dialect
from mashumaro.exceptions import UnresolvedTypeReferenceError

__all__ = ["compile_mixin_packer", "compile_mixin_unpacker"]


def compile_mixin_packer(
    cls: Type,
    format_name: str = "dict",
    dialect: Type[Dialect] | None = None,
    encoder: Any = None,
    encoder_kwargs: dict[str, dict[str, tuple[str, Any]]] | None = None,
) -> None:
    builder = CodeBuilder(
        cls=cls,
        format_name=format_name,
        encoder=encoder,
        encoder_kwargs=encoder_kwargs,
        default_dialect=dialect,
    )
    config = builder.get_config()
    try:
        builder.add_pack_method()
    except UnresolvedTypeReferenceError:
        if not config.allow_postponed_evaluation:
            raise


def compile_mixin_unpacker(
    cls: Type,
    format_name: str = "dict",
    dialect: Type[Dialect] | None = None,
    decoder: Any = None,
) -> None:
    builder = CodeBuilder(
        cls=cls,
        format_name=format_name,
        decoder=decoder,
        default_dialect=dialect,
    )
    config = builder.get_config()
    try:
        builder.add_unpack_method()
    except UnresolvedTypeReferenceError:
        if not config.allow_postponed_evaluation:
            raise
