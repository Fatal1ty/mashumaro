import dataclasses
import enum
import re
import types
import typing
from contextlib import suppress

# noinspection PyProtectedMember
from dataclasses import _FIELDS  # type: ignore

import typing_extensions

from mashumaro.core.const import PY_37, PY_38, PY_38_MIN, PY_39_MIN, PY_310_MIN
from mashumaro.dialect import Dialect

NoneType = type(None)
DataClassDictMixinPath = (
    f"{__name__.rsplit('.', 3)[:-3][0]}" f".mixins.dict.DataClassDictMixin"
)


def get_type_origin(t):
    try:
        return t.__origin__
    except AttributeError:
        return t


def is_builtin_type(t) -> bool:
    try:
        return t.__module__ == "builtins"
    except AttributeError:
        return False


def get_generic_name(t, short: bool = False) -> str:
    name = getattr(t, "_name", None)
    if name is None:
        origin = get_type_origin(t)
        if origin is t:
            return type_name(origin, short, is_type_origin=True)
        else:
            return get_generic_name(origin, short)
    if short:
        return name
    else:
        return f"{t.__module__}.{name}"


def get_args(t: typing.Any) -> typing.Tuple[typing.Any, ...]:
    return getattr(t, "__args__", None) or ()


def _get_args_str(
    t: typing.Any,
    short: bool,
    type_vars: typing.Optional[typing.Dict[str, typing.Any]] = None,
    limit: typing.Optional[int] = None,
    none_type_as_none: bool = False,
    sep: str = ", ",
) -> str:
    args = get_args(t)[:limit]
    return sep.join(
        type_name(arg, short, type_vars, none_type_as_none=none_type_as_none)
        for arg in args
    )


def get_literal_values(t: typing.Any) -> typing.Tuple[typing.Any, ...]:
    values = t.__args__
    result: typing.List[typing.Any] = []
    for value in values:
        if is_literal(value):
            result.extend(get_literal_values(value))
        else:
            result.append(value)
    return tuple(result)


def _get_literal_values_str(t: typing.Any, short: bool):
    values_str = []
    for value in get_literal_values(t):
        if isinstance(value, enum.Enum):
            values_str.append(f"{type_name(type(value), short)}.{value.name}")
        elif isinstance(  # type: ignore
            value, (int, str, bytes, bool, NoneType)  # type: ignore
        ):
            values_str.append(repr(value))
    return ", ".join(values_str)


def _typing_name(
    t: str,
    short: bool = False,
    module_name: str = "typing",
) -> str:
    return t if short else f"{module_name}.{t}"


def type_name(
    t: typing.Any,
    short: bool = False,
    type_vars: typing.Optional[typing.Dict[str, typing.Any]] = None,
    is_type_origin: bool = False,
    none_type_as_none: bool = False,
) -> str:
    if type_vars is None:
        type_vars = {}
    if t is NoneType and none_type_as_none:
        return "None"
    elif t is typing.Any:
        return _typing_name("Any", short)
    elif is_optional(t, type_vars):
        args_str = type_name(
            not_none_type_arg(get_args(t), type_vars), short, type_vars
        )
        return f"{_typing_name('Optional', short)}[{args_str}]"
    elif is_union(t):
        args_str = _get_args_str(t, short, type_vars, none_type_as_none=True)
        return f"{_typing_name('Union', short)}[{args_str}]"
    elif is_annotated(t):
        return type_name(get_args(t)[0], short, type_vars)
    elif is_literal(t):
        args_str = _get_literal_values_str(t, short)
        return f"{_typing_name('Literal', short, t.__module__)}[{args_str}]"
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
    elif is_new_type(t) and not PY_310_MIN:
        # because __qualname__ and __module__ are messed up
        t = t.__supertype__
    try:
        if short:
            return t.__qualname__
        else:
            return f"{t.__module__}.{t.__qualname__}"
    except AttributeError:
        return str(t)


def is_special_typing_primitive(t) -> bool:
    try:
        issubclass(t, object)
        return False
    except TypeError:
        return True


def is_generic(t) -> bool:
    if PY_37 or PY_38:
        # noinspection PyProtectedMember
        # noinspection PyUnresolvedReferences
        return issubclass(t.__class__, typing._GenericAlias)  # type: ignore
    elif PY_39_MIN:
        # noinspection PyProtectedMember
        # noinspection PyUnresolvedReferences
        if (
            issubclass(t.__class__, typing._BaseGenericAlias)  # type: ignore
            or type(t) is types.GenericAlias  # type: ignore
        ):
            return True
        else:  # for PEP 585 generics without args
            try:
                return (
                    hasattr(t, "__class_getitem__")
                    and type(t[str]) is types.GenericAlias  # type: ignore
                )
            except (TypeError, AttributeError):
                return False
    else:
        raise NotImplementedError


def is_typed_dict(t) -> bool:
    for module in (typing, typing_extensions):
        with suppress(AttributeError):
            if type(t) is getattr(module, "_TypedDictMeta"):
                return True
    return False


def is_named_tuple(t) -> bool:
    try:
        return issubclass(t, typing.Tuple) and hasattr(  # type: ignore
            t, "_fields"
        )
    except TypeError:
        return False


def is_new_type(t) -> bool:
    return hasattr(t, "__supertype__")


def is_union(t):
    try:
        if PY_310_MIN and isinstance(t, types.UnionType):
            return True
        return t.__origin__ is typing.Union
    except AttributeError:
        return False


def is_optional(
    t,
    type_vars: typing.Optional[typing.Dict[str, typing.Any]] = None,
) -> bool:
    if type_vars is None:
        type_vars = {}
    if not is_union(t):
        return False
    args = get_args(t)
    if len(args) != 2:
        return False
    for arg in args:
        if type_vars.get(arg, arg) is NoneType:
            return True
    return False


def is_annotated(t) -> bool:
    for module in (typing, typing_extensions):
        with suppress(AttributeError):
            if type(t) is getattr(module, "_AnnotatedAlias"):
                return True
    return False


def is_literal(t) -> bool:
    if PY_37 or PY_38:
        with suppress(AttributeError):
            return is_generic(t) and get_generic_name(t, True) == "Literal"
    elif PY_39_MIN:
        with suppress(AttributeError):
            # noinspection PyProtectedMember
            # noinspection PyUnresolvedReferences
            return type(t) is typing._LiteralGenericAlias  # type: ignore
    return False


def not_none_type_arg(
    args: typing.Tuple[typing.Any, ...],
    type_vars: typing.Optional[typing.Dict[str, typing.Any]] = None,
):
    if type_vars is None:
        type_vars = {}
    for arg in args:
        if type_vars.get(arg, arg) is not NoneType:
            return arg


def is_type_var(t) -> bool:
    return hasattr(t, "__constraints__")


def is_type_var_any(t) -> bool:
    if not is_type_var(t):
        return False
    elif t.__constraints__ != ():
        return False
    elif t.__bound__ not in (None, typing.Any):
        return False
    else:
        return True


def is_class_var(t) -> bool:
    return get_type_origin(t) is typing.ClassVar


def is_init_var(t) -> bool:
    if PY_37:
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


def is_dataclass_dict_mixin(t) -> bool:
    return type_name(t) == DataClassDictMixinPath


def is_dataclass_dict_mixin_subclass(t) -> bool:
    with suppress(AttributeError):
        for cls in t.__mro__:
            if is_dataclass_dict_mixin(cls):
                return True
    return False


def get_orig_bases(cls):
    return getattr(cls, "__orig_bases__", ())


def resolve_type_vars(cls, arg_types=()):
    arg_types = iter(arg_types)
    type_vars = {}
    result = {cls: type_vars}
    orig_bases = {
        get_type_origin(orig_base): orig_base
        for orig_base in get_orig_bases(cls)
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
        result.update(resolve_type_vars(base, base_arg_types))
    return result


def get_name_error_name(e: NameError) -> str:
    if PY_310_MIN:
        return e.name  # type: ignore
    else:
        match = re.search("'(.*)'", e.args[0])
        return match.group(1) if match else ""


def is_dialect_subclass(t) -> bool:
    try:
        return issubclass(t, Dialect)
    except TypeError:
        return False


def is_self(t) -> bool:
    return t is typing_extensions.Self


def is_required(t) -> bool:
    return get_type_origin(t) is typing_extensions.Required  # noqa


def is_not_required(t) -> bool:
    return get_type_origin(t) is typing_extensions.NotRequired  # noqa


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
    "not_none_type_arg",
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
    "is_dialect_subclass",
    "is_new_type",
    "is_annotated",
    "is_literal",
    "get_literal_values",
    "is_self",
    "is_required",
    "is_not_required",
]
