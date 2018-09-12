import sys
import enum
import typing
import datetime
# noinspection PyUnresolvedReferences
import builtins
from dataclasses import is_dataclass, MISSING
try:
    from typing import GenericMeta as Generic
except ImportError:  # python 3.7
    from typing import _GenericAlias as Generic

# noinspection PyUnresolvedReferences
from mashumaro.exceptions import MissingField


def is_generic(type_):
    return isinstance(type_, Generic)


if sys.version_info.minor == 6:

    def is_generic_list(type_):
        return type_.__extra__ is list

    def is_generic_dict(type_):
        return type_.__extra__ is dict

    def is_generic_union(type_):
        return type_.__extra__ is typing.Union

elif sys.version_info.minor == 7:

    def is_generic_list(type_):
        return type_.__origin__ is list

    def is_generic_dict(type_):
        return type_.__origin__ is dict

    def is_generic_union(type_):
        return type_.__origin__ is typing.Union

else:
    raise RuntimeError(
        "Python %d.%d.%d is not supported by mashumaro" %
        (sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
    )


class indent:

    current = ''

    def __enter__(self):
        indent.current += ' ' * 4

    def __exit__(self, exc_type, exc_val, exc_tb):
        indent.current = indent.current[:-4]


def add_from_dict(cls):

    def type_name(type_):
        if type_ is typing.Any:
            return str(type_)
        elif is_generic(type_):
            return str(type_)
        else:
            return f"{type_.__module__}.{type_.__name__}"

    def add_line(line):
        lines.append(f"{indent.current}{line}")

    def set_field_value(fname, ftype):
        if is_dataclass(ftype):
            add_line(f"if not isinstance(value, dict):")
            with indent():
                add_line(f"raise TypeError('{fname} value should be "
                         f"a dictionary object not %s' % type(value))")
            add_line(f"kwargs['{fname}'] = "
                     f"{type_name(ftype)}.from_dict(value)")
        elif is_generic(ftype):
            if is_generic_list(ftype):
                arg_type, *_ = ftype.__args__
                # TODO: Добавить поддержку Union
                # TODO: добавить поддержку Dict
                # TODO: добавить поддержку Collection
                arg_type_name = arg_type.__name__
                if is_dataclass(arg_type):
                    add_line(f"if not isinstance(value, list):")
                    with indent():
                        add_line(f"raise TypeError('{fname} should be "
                                 f"a list object not %s' % type(value))")
                    add_line(f"kwargs['{fname}'] = [{arg_type_name}"
                             f".from_dict(v) for v in value]")
                else:
                    add_line(f"kwargs['{fname}'] = value")
            elif is_generic_union(ftype):
                add_line(f"kwargs['{fname}'] = value")
        elif ftype is datetime.datetime:
            add_line(f"if isinstance(value, datetime.datetime):")
            with indent():
                add_line(f"kwargs['{fname}'] = value")
            add_line(f"else:")
            with indent():
                add_line(f"kwargs['{fname}'] = "
                         f"datetime.datetime.utcfromtimestamp(value)")
        elif ftype is not typing.Any and issubclass(ftype, enum.Enum):
            add_line(f"kwargs['{fname}'] = {type_name(ftype)}(value)")
        else:
            add_line(f"kwargs['{fname}'] = value")

    namespace = cls.__dict__
    fields = namespace.get('__annotations__')
    if not fields:
        return

    defaults = {name: namespace.get(name, MISSING) for name in fields}
    lines = list()
    modules = set()
    exclude = {'builtins', 'typing', 'datetime'}

    add_line("@classmethod")
    add_line("def from_dict(cls, d: typing.Mapping):")
    with indent():
        add_line("kwargs = {}")
        for field_name, field_type in fields.items():
            if field_type.__module__ not in modules:
                if field_type.__module__ not in exclude:
                    modules.add(field_type.__module__)
                    add_line(f"import {field_type.__module__}")
                    add_line(f"globals()['{field_type.__module__}'] = "
                             f"{field_type.__module__}")
            add_line(f"value = d.get('{field_name}', MISSING)")
            if defaults[field_name] is MISSING:
                add_line(f"if value is MISSING:")
                with indent():
                    add_line(f"raise MissingField('{field_name}',"
                             f"{type_name(field_type)},cls)")
                add_line(f"else:")
                with indent():
                    set_field_value(field_name, field_type)
            else:
                add_line("if value is not MISSING:")
                with indent():
                    set_field_value(field_name, field_type)
        add_line("return cls(**kwargs)")
    add_line(f"setattr(cls, 'from_dict', from_dict)")

    exec("\n".join(lines), globals(), locals())


def add_to_dict(cls):

    def add_line(line):
        lines.append(f"{indent.current}{line}")

    namespace = cls.__dict__
    fields = namespace.get('__annotations__')
    if not fields:
        return

    defaults = {name: namespace.get(name, MISSING) for name in fields}
    lines = list()
    modules = set()
    exclude = {'builtins', 'typing', 'datetime'}

    add_line("def to_dict(self):")
    with indent():
        add_line("kwargs = {}")
        for field_name, field_type in fields.items():
            add_line(f"value = getattr(self, '{field_name}')")
            if is_dataclass(field_type):
                add_line(f"kwargs['{field_name}'] = value.to_dict()")
            elif is_generic(field_type):
                arg_type, *_ = field_type.__args__
                # TODO: Добавить поддержку Union
                # TODO: добавить поддержку Dict
                # TODO: добавить поддержку Collection
                if is_generic_list(field_type):
                    if is_dataclass(arg_type):
                        add_line(f"kwargs['{field_name}'] = "
                                 f"[v.to_dict() for v in value]")
                elif is_generic_union(field_type):
                    add_line(f"kwargs['{field_name}'] = value.value")
            else:
                add_line(f"kwargs['{field_name}'] = value")
        add_line("return kwargs")
    add_line(f"setattr(cls, 'to_dict', to_dict)")

    exec("\n".join(lines), globals(), locals())


__all__ = [add_from_dict, add_to_dict, is_generic]
