from typing import Any, Dict, Optional, Tuple, Type

from mashumaro.core.meta.builder import CodeBuilder
from mashumaro.dialect import Dialect
from mashumaro.exceptions import UnresolvedTypeReferenceError


def compile_mixin_packer(
    cls,
    format_name: str = "dict",
    dialect: Optional[Type[Dialect]] = None,
    encoder: Any = None,
    encoder_kwargs: Optional[Dict[str, Dict[str, Tuple[str, Any]]]] = None,
):
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
    cls,
    format_name: str = "dict",
    dialect: Optional[Type[Dialect]] = None,
    decoder: Any = None,
):
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


__all__ = ["compile_mixin_packer", "compile_mixin_unpacker"]
