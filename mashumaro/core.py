import sys
import datetime
import builtins
from enum import Enum
from typing import Mapping, Union, Any
from dataclasses import is_dataclass, MISSING
try:
    from typing import GenericMeta as Generic
except ImportError:  # python 3.7
    from typing import _GenericAlias as Generic

import msgpack
import yaml


def is_generic(type_):
    return isinstance(type_, Generic)


if sys.version_info.minor == 6:

    def is_generic_list(type_):
        return type_.__extra__ is list

    def is_generic_dict(type_):
        return type_.__extra__ is dict

    def is_generic_union(type_):
        return type_.__extra__ is Union

elif sys.version_info.minor == 7:

    def is_generic_list(type_):
        return type_.__origin__ is list

    def is_generic_dict(type_):
        return type_.__origin__ is dict

    def is_generic_union(type_):
        return type_.__origin__ is Union


class indent:

    current = ''

    def __enter__(self):
        indent.current += ' ' * 4

    def __exit__(self, exc_type, exc_val, exc_tb):
        indent.current = indent.current[:-4]


def default_packer(o):
    if isinstance(o, datetime.datetime):
        return o.timestamp()


class MissingField(Exception):
    def __init__(self, field_name, field_type, holder_class):
        self.field_name = field_name
        self.field_type = field_type
        self.holder_class = holder_class

    @property
    def field_type_name(self):
        if is_generic(self.field_type):
            return str(self.field_type)
        else:
            return f"{self.field_type.__module__}.{self.field_type.__name__}"

    @property
    def holder_class_name(self):
        return self.holder_class.__name__
        # return f"{self.holder_class.__module__}." \
        #        f"{self.holder_class.__name__}"

    def __str__(self):
        return f'Field "{self.field_name}" of type {self.field_type_name}' \
               f' is missing in {self.holder_class} instance'


def add_from_dict(cls):

    def type_name(type_):
        if type_ is Any:
            return str(type_)
            # return f"{type_module}.Any"
        elif is_generic(type_):
            return str(type_)
            # return "f{type_module}.{str(type_)}"
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
                arg_type, = ftype.__args__
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
            # TODO: добавить Generic Dict
        elif ftype is datetime.datetime:
            add_line(f"if isinstance(value, datetime.datetime):")
            with indent():
                add_line(f"kwargs['{fname}'] = value")
            add_line(f"else:")
            with indent():
                add_line(f"kwargs['{fname}'] = "
                         f"datetime.datetime.utcfromtimestamp(value)")
        elif ftype is not Any and issubclass(ftype, Enum):
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
    add_line("def from_dict(cls, d: Mapping):")
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

    # print('\n'.join(lines))
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
                arg_type, = field_type.__args__
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


class DataClassDictMixin:
    def __init_subclass__(cls, **kwargs):
        add_from_dict(cls)
        add_to_dict(cls)

    def to_dict(self) -> dict:
        pass

    @classmethod
    def from_dict(cls, d: Mapping):
        pass


class DataClassMessagePackMixin(DataClassDictMixin):
    def to_msgpack(self):
        return msgpack.packb(
            self.to_dict(), default=default_packer, use_bin_type=True)

    @classmethod
    def from_msgpack(cls, data: bytes):
        return cls.from_dict(msgpack.unpackb(data, raw=False))


class DataClassYAMLMixin(DataClassDictMixin):
    def to_yaml(self):
        return yaml.dump(self.to_dict())

    @classmethod
    def from_yaml(cls, data: bytes):
        return cls.from_dict(yaml.load(data))


__all__ = [DataClassDictMixin, DataClassMessagePackMixin, DataClassYAMLMixin]
