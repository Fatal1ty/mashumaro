import dataclasses
import inspect
import re
import types
import typing
from contextlib import suppress

# noinspection PyProtectedMember
from dataclasses import _FIELDS  # type: ignore

import typing_extensions

from .macros import (
    PY_36,
    PY_37,
    PY_37_MIN,
    PY_38,
    PY_38_MIN,
    PY_39_MIN,
    PY_310_MIN,
)

DataClassDictMixinPath = "mashumaro.serializer.base.dict.DataClassDictMixin"
NoneType = type(None)


def get_type_origin(t):
    origin = None
    try:
        if PY_36:
            origin = t.__extra__ or t.__origin__
        elif PY_37_MIN:
            origin = t.__origin__
    except AttributeError:
        origin = t
    return origin or t


def is_builtin_type(t):
    try:
        return t.__module__ == "builtins"
    except AttributeError:
        return False


def get_generic_name(t, short: bool = False):
    if PY_36:
        name = getattr(t, "__name__")
    elif PY_37_MIN:
        name = getattr(t, "_name", None)
        if name is None:
            return type_name(get_type_origin(t), short, is_type_origin=True)
    if short:
        return name
    else:
        return f"{t.__module__}.{name}"


def get_args(t: typing.Any):
    return getattr(t, "__args__", None) or ()


def _get_args_str(
    t: typing.Any,
    short: bool,
    type_vars: typing.Dict[str, typing.Any] = None,
    limit: typing.Optional[int] = None,
):
    args = get_args(t)[:limit]
    return ", ".join(type_name(arg, short, type_vars) for arg in args)


def _typing_name(t: str, short: bool = False):
    return t if short else f"typing.{t}"


def type_name(
    t: typing.Any,
    short: bool = False,
    type_vars: typing.Dict[str, typing.Any] = None,
    is_type_origin: bool = False,
) -> str:
    if type_vars is None:
        type_vars = {}
    if t is typing.Any:
        return _typing_name("Any", short)
    elif is_optional(t):
        args_str = _get_args_str(t, short, type_vars, 1)
        return f"{_typing_name('Optional', short)}[{args_str}]"
    elif is_union(t):
        args_str = _get_args_str(t, short, type_vars)
        return f"{_typing_name('Union', short)}[{args_str}]"
    elif is_generic(t) and not is_type_origin:
        args_str = _get_args_str(t, short, type_vars)
        if not args_str:
            return get_generic_name(t, short)
        else:
            return f"{get_generic_name(t, short)}[{args_str}]"
    elif is_builtin_type(t):
        return t.__qualname__
    elif is_type_var(t):
        if t in type_vars and type_vars[t] is not t:
            return type_name(type_vars[t], short, type_vars)
        elif is_type_var_any(t):
            return _typing_name("Any", short)
        constraints = getattr(t, "__constraints__")
        if constraints:
            args_str = ", ".join(
                type_name(c, short, type_vars) for c in constraints
            )
            return f"{_typing_name('Union', short)}[{args_str}]"
        else:
            bound = getattr(t, "__bound__")
            return type_name(bound, short, type_vars)
    else:
        try:
            if short:
                return t.__qualname__
            else:
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
    elif PY_39_MIN:
        # noinspection PyProtectedMember
        # noinspection PyUnresolvedReferences
        if (
            issubclass(t.__class__, typing._BaseGenericAlias)
            or type(t) is types.GenericAlias
        ):
            return True
        else:  # for PEP 585 generics without args
            try:
                return (
                    hasattr(t, "__class_getitem__")
                    and type(t[str]) is types.GenericAlias
                )
            except (TypeError, AttributeError):
                return False
    else:
        raise NotImplementedError


def is_typed_dict(t):
    for module in (typing, typing_extensions):
        with suppress(AttributeError):
            if type(t) is getattr(module, "_TypedDictMeta"):
                return True
    return False


def is_named_tuple(t):
    try:
        return issubclass(t, typing.Tuple) and hasattr(t, "_fields")
    except TypeError:
        return False


def is_union(t):
    try:
        return t.__origin__ is typing.Union
    except AttributeError:
        return False


def is_optional(t):
    if not is_union(t):
        return False
    args = get_args(t)
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
    elif PY_37_MIN:
        return get_type_origin(t) is typing.ClassVar
    else:
        raise NotImplementedError


def is_init_var(t):
    if PY_36 or PY_37:
        return get_type_origin(t) is dataclasses.InitVar
    elif PY_38_MIN:
        return isinstance(t, dataclasses.InitVar)
    else:
        raise NotImplementedError


def get_class_that_defines_method(method_name, cls):
    for cls in cls.__mro__:
        if method_name in cls.__dict__:
            return cls


def get_class_that_defines_field(field_name, cls):
    prev_cls = None
    prev_field = None
    for base in reversed(cls.__mro__):
        if dataclasses.is_dataclass(base):
            field = getattr(base, _FIELDS).get(field_name)
            if field and field != prev_field:
                prev_field = field
                prev_cls = base
    return prev_cls or cls


def is_dataclass_dict_mixin(t):
    return type_name(t) == DataClassDictMixinPath


def is_dataclass_dict_mixin_subclass(t):
    with suppress(AttributeError):
        for cls in t.__mro__:
            if is_dataclass_dict_mixin(cls):
                return True
    return False


def get_orig_bases(cls, is_created=True):
    if PY_36 and not is_created:
        # on py3.6 __orig_bases__ is correct only after the class is created
        for record in inspect.stack():
            if (
                record.filename.endswith("typing.py")
                and record.function == "__new__"
                and record.frame.f_locals.get("cls") is typing.GenericMeta
                and record.frame.f_locals.get("initial_bases")
                and record.frame.f_locals.get("namespace", {}).get(
                    "__qualname__"
                )
                == cls.__qualname__
            ):
                return record.frame.f_locals.get("initial_bases")
    return getattr(cls, "__orig_bases__", ())


def resolve_type_vars(cls, arg_types=(), is_cls_created=False):
    arg_types = iter(arg_types)
    type_vars = {}
    result = {cls: type_vars}
    orig_bases = {
        get_type_origin(orig_base): orig_base
        for orig_base in get_orig_bases(cls, is_cls_created)
    }
    for base in getattr(cls, "__bases__", ()):
        orig_base = orig_bases.get(get_type_origin(base))
        base_args = get_args(orig_base)
        for base_arg in base_args:
            if is_type_var(base_arg):
                if base_arg not in type_vars:
                    try:
                        next_arg_type = next(arg_types)
                    except StopIteration:
                        next_arg_type = base_arg
                    type_vars[base_arg] = next_arg_type
        base_arg_types = (
            type_vars.get(base_arg, base_arg) for base_arg in base_args
        )
        result.update(resolve_type_vars(base, base_arg_types, True))
    return result


def get_name_error_name(e: NameError) -> str:
    if PY_310_MIN:
        return e.name  # type: ignore
    else:
        match = re.search("'(.*)'", e.args[0])
        return match.group(1) if match else ""


__all__ = [
    "get_type_origin",
    "get_args",
    "type_name",
    "is_special_typing_primitive",
    "is_generic",
    "is_typed_dict",
    "is_named_tuple",
    "is_optional",
    "is_union",
    "is_type_var",
    "is_type_var_any",
    "is_class_var",
    "is_init_var",
    "get_class_that_defines_method",
    "get_class_that_defines_field",
    "is_dataclass_dict_mixin",
    "is_dataclass_dict_mixin_subclass",
    "resolve_type_vars",
    "get_generic_name",
    "get_name_error_name",
]
