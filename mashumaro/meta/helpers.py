import dataclasses
import typing
from contextlib import suppress

from .macros import PY_36, PY_37, PY_37_MIN, PY_38, PY_39

DataClassDictMixinPath = "mashumaro.serializer.base.dict.DataClassDictMixin"
NoneType = type(None)


def get_type_origin(t):
    try:
        if PY_36:
            return t.__extra__
        elif PY_37 or PY_38 or PY_39:
            return t.__origin__
    except AttributeError:
        return t


def is_builtin_type(t):
    try:
        return t.__module__ == "builtins"
    except AttributeError:
        return False


def get_generic_name(t, short: bool = False):
    if PY_36:
        name = getattr(t, "__name__")
    elif PY_37_MIN:
        name = getattr(t, "_name")
    if short:
        return name
    else:
        return f"{t.__module__}.{name}"


def _get_args_str(t, short, limit=None):
    args = (getattr(t, "__args__", None) or ())[:limit]
    return ", ".join(type_name(arg, short) for arg in args)


def _typing_name(t: str, short: bool = False):
    return t if short else f"typing.{t}"


def type_name(t, short: bool = False) -> str:
    if is_builtin_type(t):
        return t.__qualname__
    if t is typing.Any:
        return _typing_name("Any", short)
    elif is_optional(t):
        return (
            f"{_typing_name('Optional', short)}[{_get_args_str(t, short, 1)}]"
        )
    elif is_union(t):
        return f"{_typing_name('Union', short)}[{_get_args_str(t, short)}]"
    elif is_generic(t):
        args_str = _get_args_str(t, short)
        if not args_str:
            return get_generic_name(t, short)
        else:
            return f"{get_generic_name(t, short)}[{args_str}]"
    elif is_type_var_any(t):
        return _typing_name("Any", short)
    elif is_type_var(t):
        constraints = getattr(t, "__constraints__")
        if constraints:
            args_str = ", ".join(type_name(c, short) for c in constraints)
            return f"{_typing_name('Union', short)}[{args_str}]"
        else:
            bound = getattr(t, "__bound__")
            return type_name(bound, short)
    else:
        try:
            return f"{t.__module__}.{t.__qualname__}"
        except AttributeError:
            return str(t)


def is_special_typing_primitive(t):
    try:
        issubclass(t, object)
        return False
    except TypeError:
        return True


def is_generic(t):
    if PY_36:
        # noinspection PyUnresolvedReferences
        return issubclass(t.__class__, typing.GenericMeta)
    elif PY_37 or PY_38:
        # noinspection PyProtectedMember
        # noinspection PyUnresolvedReferences
        return t.__class__ in (
            typing._GenericAlias,
            typing._VariadicGenericAlias,
        )
    elif PY_39:
        # noinspection PyProtectedMember
        # noinspection PyUnresolvedReferences
        return issubclass(t.__class__, typing._BaseGenericAlias)
    else:
        raise NotImplementedError


def is_union(t):
    try:
        return t.__origin__ is typing.Union
    except AttributeError:
        return False


def is_optional(t):
    if not is_union(t):
        return False
    args = getattr(t, "__args__", ())
    return len(args) == 2 and args[1] == NoneType


def is_type_var(t):
    return hasattr(t, "__constraints__")


def is_type_var_any(t):
    if not is_type_var(t):
        return False
    elif t.__constraints__ != ():
        return False
    elif t.__bound__ not in (None, typing.Any):
        return False
    else:
        return True


def is_class_var(t):
    if PY_36:
        return (
            is_special_typing_primitive(t) and type(t).__name__ == "_ClassVar"
        )
    elif PY_37 or PY_38 or PY_39:
        return get_type_origin(t) is typing.ClassVar
    else:
        raise NotImplementedError


def is_init_var(t):
    if PY_36 or PY_37:
        return get_type_origin(t) is dataclasses.InitVar
    elif PY_38 or PY_39:
        return isinstance(t, dataclasses.InitVar)
    else:
        raise NotImplementedError


def get_class_that_define_method(method_name, cls):
    for cls in cls.__mro__:
        if method_name in cls.__dict__:
            return cls


def is_dataclass_dict_mixin(t):
    return type_name(t) == DataClassDictMixinPath


def is_dataclass_dict_mixin_subclass(t):
    with suppress(AttributeError):
        for cls in t.__mro__:
            if is_dataclass_dict_mixin(cls):
                return True
    return False


__all__ = [
    "get_type_origin",
    "type_name",
    "is_special_typing_primitive",
    "is_generic",
    "is_optional",
    "is_union",
    "is_type_var",
    "is_type_var_any",
    "is_class_var",
    "is_init_var",
    "get_class_that_define_method",
    "is_dataclass_dict_mixin",
    "is_dataclass_dict_mixin_subclass",
]
