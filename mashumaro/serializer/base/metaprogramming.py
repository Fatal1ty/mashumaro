import enum
import uuid
import typing
# noinspection PyUnresolvedReferences
import builtins
import datetime
import collections
import collections.abc
from decimal import Decimal
from fractions import Fraction
from contextlib import suppress
# noinspection PyUnresolvedReferences
from base64 import encodebytes, decodebytes
from contextlib import contextmanager
from dataclasses import is_dataclass, MISSING

# noinspection PyUnresolvedReferences
from mashumaro.exceptions import MissingField, UnserializableField,\
    UnserializableDataError
from mashumaro.meta.patch import patch_fromisoformat
from mashumaro.meta.helpers import *
from mashumaro.types import SerializableType, SerializationStrategy


patch_fromisoformat()


NoneType = type(None)
INITIAL_MODULES = get_imported_module_names()


class CodeBuilder:
    def __init__(self, cls):
        self.cls = cls
        self.lines = None            # type: typing.Optional[typing.List[str]]
        self.modules = None          # type: typing.Optional[typing.Set[str]]
        self.globals = None          # type: typing.Set[str]
        self._current_indent = None  # type: typing.Optional[str]

    def reset(self):
        self.lines = []
        self.modules = INITIAL_MODULES.copy()
        self.globals = set()
        self._current_indent = ''

    @property
    def namespace(self):
        return self.cls.__dict__

    @property
    def fields(self):
        fields = {}
        for fname, ftype in typing.get_type_hints(self.cls).items():
            if is_class_var(ftype) or is_init_var(ftype):
                continue
            fields[fname] = ftype
        return fields

    @property
    def defaults(self):
        return {name: self.namespace.get(name, MISSING) for name in self.fields}

    def _add_type_modules(self, *types_):
        for t in types_:
            module = getattr(t, '__module__', None)
            if not module:
                continue
            if module not in self.modules:
                self.modules.add(module)
                self.add_line(f"if '{module}' not in globals():")
                with self.indent():
                    self.add_line(f"import {module}")
                root_module = module.split('.')[0]
                if root_module not in self.globals:
                    self.globals.add(root_module)
                    self.add_line('else:')
                    with self.indent():
                        self.add_line(f"global {root_module}")
            args = getattr(t, '__args__', ())
            if args:
                self._add_type_modules(*args)
            constraints = getattr(t, '__constraints__', ())
            if constraints:
                self._add_type_modules(*constraints)

    def add_line(self, line):
        self.lines.append(f"{self._current_indent}{line}")

    @contextmanager
    def indent(self):
        self._current_indent += ' ' * 4
        try:
            yield
        finally:
            self._current_indent = self._current_indent[:-4]

    def compile(self):
        exec("\n".join(self.lines), globals(), self.__dict__)

    def add_from_dict(self):

        self.reset()
        self.add_line('@classmethod')
        self.add_line("def from_dict(cls, d, use_bytes=False, use_enum=False, "
                      "use_datetime=False):")
        with self.indent():
            self.add_line('try:')
            with self.indent():
                self.add_line("kwargs = {}")
                for fname, ftype in self.fields.items():
                    self._add_type_modules(ftype)
                    self.add_line(f"value = d.get('{fname}', MISSING)")
                    self.add_line("if value is None:")
                    with self.indent():
                        self.add_line(f"kwargs['{fname}'] = None")
                    self.add_line("else:")
                    with self.indent():
                        if self.defaults[fname] is MISSING:
                            self.add_line(f"if value is MISSING:")
                            with self.indent():
                                if isinstance(ftype, SerializationStrategy):
                                    self.add_line(
                                        f"raise MissingField('{fname}',"
                                        f"{type_name(ftype.__class__)},cls)")
                                else:
                                    self.add_line(
                                        f"raise MissingField('{fname}',"
                                        f"{type_name(ftype)},cls)")
                            self.add_line("else:")
                            with self.indent():
                                unpacked_value = self._unpack_field_value(
                                    fname, ftype, self.cls)
                                self.add_line(
                                    f"kwargs['{fname}'] = {unpacked_value}")
                        else:
                            self.add_line("if value is not MISSING:")
                            with self.indent():
                                unpacked_value = self._unpack_field_value(
                                    fname, ftype, self.cls)
                                self.add_line(
                                    f"kwargs['{fname}'] = {unpacked_value}")
            self.add_line('except AttributeError:')
            with self.indent():
                self.add_line('if not isinstance(d, dict):')
                with self.indent():
                    self.add_line(f"raise ValueError('Argument for "
                                  f"{type_name(self.cls)}.from_dict method "
                                  f"should be a dict instance') from None")
                self.add_line('else:')
                with self.indent():
                    self.add_line('raise')
            self.add_line("return cls(**kwargs)")
        self.add_line(f"setattr(cls, 'from_dict', from_dict)")
        self.compile()

    def add_to_dict(self):

        self.reset()
        self.add_line("def to_dict(self, use_bytes=False, use_enum=False, "
                      "use_datetime=False):")
        with self.indent():
            self.add_line("kwargs = {}")
            for fname, ftype in self.fields.items():
                self.add_line(f"value = getattr(self, '{fname}')")
                self.add_line('if value is None:')
                with self.indent():
                    self.add_line(f"kwargs['{fname}'] = None")
                self.add_line('else:')
                with self.indent():
                    packed_value = self._pack_value(fname, ftype, self.cls)
                    self.add_line(f"kwargs['{fname}'] = {packed_value}")
            self.add_line("return kwargs")
        self.add_line(f"setattr(cls, 'to_dict', to_dict)")
        self.compile()

    def _pack_value(self, fname, ftype, parent, value_name='value'):

        if is_dataclass(ftype):
            return f"{value_name}.to_dict(use_bytes, use_enum, use_datetime)"

        with suppress(TypeError):
            if issubclass(ftype, SerializableType):
                return f'{value_name}._serialize()'
        if isinstance(ftype, SerializationStrategy):
            return f"self.__dataclass_fields__['{fname}'].type" \
                f"._serialize({value_name})"

        origin_type = get_type_origin(ftype)
        if is_special_typing_primitive(origin_type):
            if origin_type is typing.Any:
                return value_name
            elif is_union(ftype):
                args = getattr(ftype, '__args__', ())
                if len(args) == 2 and args[1] == NoneType:  # it is Optional
                    return self._pack_value(fname, args[0], parent)
                else:
                    raise UnserializableDataError(
                        'Unions are not supported by mashumaro')
            elif origin_type is typing.AnyStr:
                raise UnserializableDataError(
                    'AnyStr is not supported by mashumaro')
            elif is_type_var(ftype):
                raise UnserializableDataError(
                    'TypeVars are not supported by mashumaro')
            else:
                raise UnserializableDataError(
                    f'{ftype} as a field type is not supported by mashumaro')
        elif issubclass(origin_type, typing.Collection):
            args = getattr(ftype, '__args__', ())

            def inner_expr(arg_num=0, v_name='value'):
                return self._pack_value(fname, args[arg_num], parent, v_name)

            if issubclass(origin_type, (typing.List,
                                        typing.Deque,
                                        typing.Tuple,
                                        typing.AbstractSet)):
                if is_generic(ftype):
                    return f'[{inner_expr()} for value in {value_name}]'
                elif ftype is list:
                    raise UnserializableField(
                        fname, ftype, parent, 'Use typing.List[T] instead')
                elif ftype is collections.deque:
                    raise UnserializableField(
                        fname, ftype, parent, 'Use typing.Deque[T] instead')
                elif ftype is tuple:
                    raise UnserializableField(
                        fname, ftype, parent, 'Use typing.Tuple[T] instead')
                elif ftype is set:
                    raise UnserializableField(
                        fname, ftype, parent, 'Use typing.Set[T] instead')
                elif ftype is frozenset:
                    raise UnserializableField(
                        fname, ftype, parent, 'Use typing.FrozenSet[T] instead')
            elif issubclass(origin_type, typing.ChainMap):
                if ftype is collections.ChainMap:
                    raise UnserializableField(
                        fname, ftype, parent,
                        'Use typing.ChainMap[KT,VT] instead'
                    )
                elif is_generic(ftype):
                    if is_dataclass(args[0]):
                        raise UnserializableDataError(
                            'ChainMaps with dataclasses as keys '
                            'are not supported by mashumaro')
                    else:
                        return f'[{{{inner_expr(0,"key")}:{inner_expr(1)} ' \
                               f'for key,value in m.items()}} ' \
                               f'for m in value.maps]'
            elif issubclass(origin_type, typing.Mapping):
                if ftype is dict:
                    raise UnserializableField(
                        fname, ftype, parent,
                        'Use typing.Dict[KT,VT] or Mapping[KT,VT] instead'
                    )
                elif is_generic(ftype):
                    if is_dataclass(args[0]):
                        raise UnserializableDataError(
                            'Mappings with dataclasses as keys '
                            'are not supported by mashumaro')
                    else:
                        return f'{{{inner_expr(0,"key")}: {inner_expr(1)} ' \
                               f'for key, value in {value_name}.items()}}'
            elif issubclass(origin_type, typing.ByteString):
                return f'{value_name} if use_bytes else ' \
                       f'encodebytes({value_name}).decode()'
            elif issubclass(origin_type, str):
                return value_name
            elif issubclass(origin_type, typing.Sequence):
                if is_generic(ftype):
                    return f'[{inner_expr()} for value in {value_name}]'
        elif issubclass(origin_type, enum.Enum):
            return f'{value_name} if use_enum else {value_name}.value'
        elif origin_type is int:
            return f'int({value_name})'
        elif origin_type is float:
            return f'float({value_name})'
        elif origin_type in (bool, NoneType):
            return value_name
        elif origin_type in (datetime.datetime, datetime.date, datetime.time):
            return f'{value_name} if use_datetime else {value_name}.isoformat()'
        elif origin_type is datetime.timedelta:
            return f'{value_name}.total_seconds()'
        elif origin_type is uuid.UUID:
            return f'str({value_name})'
        elif origin_type is Decimal:
            return f'str({value_name})'
        elif origin_type is Fraction:
            return f'str({value_name})'

        raise UnserializableField(fname, ftype, parent)

    def _unpack_field_value(self, fname, ftype, parent, value_name='value'):

        if is_dataclass(ftype):
            return f"{type_name(ftype)}.from_dict({value_name}, " \
                   f"use_bytes, use_enum, use_datetime)"

        with suppress(TypeError):
            if issubclass(ftype, SerializableType):
                return f'{type_name(ftype)}._deserialize({value_name})'
        if isinstance(ftype, SerializationStrategy):
            return f"cls.__dataclass_fields__['{fname}'].type" \
                f"._deserialize({value_name})"

        origin_type = get_type_origin(ftype)
        if is_special_typing_primitive(origin_type):
            if origin_type is typing.Any:
                return value_name
            elif is_union(ftype):
                args = getattr(ftype, '__args__', ())
                if len(args) == 2 and args[1] == NoneType:  # it is Optional
                    return self._unpack_field_value(fname, args[0], parent)
                else:
                    raise UnserializableDataError(
                        'Unions are not supported by mashumaro')
            elif origin_type is typing.AnyStr:
                raise UnserializableDataError(
                    'AnyStr is not supported by mashumaro')
            elif is_type_var(ftype):
                raise UnserializableDataError(
                    'TypeVars are not supported by mashumaro')
            else:
                raise UnserializableDataError(
                    f'{ftype} as a field type is not supported by mashumaro')
        elif issubclass(origin_type, typing.Collection):
            args = getattr(ftype, '__args__', ())

            def inner_expr(arg_num=0, v_name='value'):
                return self._unpack_field_value(
                    fname, args[arg_num], parent, v_name)

            if issubclass(origin_type, typing.List):
                if is_generic(ftype):
                    return f'[{inner_expr()} for value in {value_name}]'
                elif ftype is list:
                    raise UnserializableField(
                        fname, ftype, parent, 'Use typing.List[T] instead')
            elif issubclass(origin_type, typing.Deque):
                if is_generic(ftype):
                    return f'collections.deque([{inner_expr()} ' \
                           f'for value in {value_name}])'
                elif ftype is collections.deque:
                    raise UnserializableField(
                        fname, ftype, parent, 'Use typing.Deque[T] instead')
            elif issubclass(origin_type, typing.Tuple):
                if is_generic(ftype):
                    return f'tuple([{inner_expr()} for value in {value_name}])'
                elif ftype is tuple:
                    raise UnserializableField(
                        fname, ftype, parent, 'Use typing.Tuple[T] instead')
            elif issubclass(origin_type, typing.FrozenSet):
                if is_generic(ftype):
                    return f'frozenset([{inner_expr()} ' \
                           f'for value in {value_name}])'
                elif ftype is frozenset:
                    raise UnserializableField(
                        fname, ftype, parent, 'Use typing.FrozenSet[T] instead')
            elif issubclass(origin_type, typing.AbstractSet):
                if is_generic(ftype):
                    return f'set([{inner_expr()} for value in {value_name}])'
                elif ftype is set:
                    raise UnserializableField(
                        fname, ftype, parent, 'Use typing.Set[T] instead')
            elif issubclass(origin_type, typing.ChainMap):
                if ftype is collections.ChainMap:
                    raise UnserializableField(
                        fname, ftype, parent,
                        'Use typing.ChainMap[KT,VT] instead'
                    )
                elif is_generic(ftype):
                    if is_dataclass(args[0]):
                        raise UnserializableDataError(
                            'ChainMaps with dataclasses as keys '
                            'are not supported by mashumaro')
                    else:
                        return f'collections.ChainMap(' \
                               f'*[{{{inner_expr(0,"key")}:{inner_expr(1)} ' \
                               f'for key, value in m.items()}} ' \
                               f'for m in {value_name}])'
            elif issubclass(origin_type, typing.Mapping):
                if ftype is dict:
                    raise UnserializableField(
                        fname, ftype, parent,
                        'Use typing.Dict[KT,VT] or Mapping[KT,VT] instead'
                    )
                elif is_generic(ftype):
                    if is_dataclass(args[0]):
                        raise UnserializableDataError(
                            'Mappings with dataclasses as keys '
                            'are not supported by mashumaro')
                    else:
                        return f'{{{inner_expr(0,"key")}: {inner_expr(1)} ' \
                               f'for key, value in {value_name}.items()}}'
            elif issubclass(origin_type, typing.ByteString):
                if origin_type is bytes:
                    return f'{value_name} if use_bytes else ' \
                           f'decodebytes({value_name}.encode())'
                elif origin_type is bytearray:
                    return f'bytearray({value_name} if use_bytes else ' \
                           f'decodebytes({value_name}.encode()))'
            elif issubclass(origin_type, str):
                return value_name
            elif issubclass(origin_type, typing.Sequence):
                if is_generic(ftype):
                    return f'[{inner_expr()} for value in {value_name}]'
        elif issubclass(origin_type, enum.Enum):
            return f'{value_name} if use_enum ' \
                   f'else {type_name(origin_type)}({value_name})'
        elif origin_type is int:
            return f'int({value_name})'
        elif origin_type is float:
            return f'float({value_name})'
        elif origin_type in (bool, NoneType):
            return value_name
        elif origin_type in (datetime.datetime, datetime.date, datetime.time):
            return f'{value_name} if use_datetime else ' \
                   f'datetime.{origin_type.__name__}.' \
                   f'fromisoformat({value_name})'
        elif origin_type is datetime.timedelta:
            return f'datetime.timedelta(seconds={value_name})'
        elif origin_type is uuid.UUID:
            return f'uuid.UUID({value_name})'
        elif origin_type is Decimal:
            return f'Decimal({value_name})'
        elif origin_type is Fraction:
            return f'Fraction({value_name})'

        raise UnserializableField(fname, ftype, parent)
