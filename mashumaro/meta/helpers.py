import types
import typing

from .macros import PY_36, PY_37


def get_imported_module_names():
    # noinspection PyUnresolvedReferences
    return {value.__name__ for value in globals().values()
            if isinstance(value, types.ModuleType)}


def get_type_origin(t):
    try:
        if PY_36:
            return t.__extra__
        elif PY_37:
            return t.__origin__
    except AttributeError:
        return t


def type_name(t):
    if is_generic(t):
        return str(t)
    else:
        try:
            return f"{t.__module__}.{t.__name__}"
        except AttributeError:
            return str(t)


def is_special_typing_primitive(t):
    try:
        issubclass(t, object)
        return False
    except TypeError:
        return True


def is_generic(t):
    if PY_37:
        # noinspection PyProtectedMember
        # noinspection PyUnresolvedReferences
        return t.__class__ is typing._GenericAlias
    elif PY_36:
        # noinspection PyUnresolvedReferences
        return issubclass(t.__class__, typing.GenericMeta)
    else:
        raise NotImplementedError


def is_union(t):
    try:
        return t.__origin__ is typing.Union
    except AttributeError:
        return False


def is_type_var(t):
    return hasattr(t, '__constraints__')


__all__ = [
    'get_imported_module_names',
    'get_type_origin',
    'type_name',
    'is_special_typing_primitive',
    'is_generic',
    'is_union',
    'is_type_var',
]
