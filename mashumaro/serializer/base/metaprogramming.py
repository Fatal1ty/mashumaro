import sys
import types
import typing
import inspect
# noinspection PyUnresolvedReferences
import builtins
import collections
import collections.abc
# noinspection PyUnresolvedReferences
from binascii import hexlify, unhexlify
from contextlib import contextmanager
from dataclasses import is_dataclass, MISSING

# noinspection PyUnresolvedReferences
from mashumaro.exceptions import MissingField, UnserializableField,\
    UnserializableDataError
from mashumaro.abc import SerializableSequence, SerializableMapping


NoneType = type(None)


def get_imported_module_names():
    # noinspection PyUnresolvedReferences
    return {value.__name__ for value in globals().values()
            if isinstance(value, types.ModuleType)}


def get_type_origin(t):
    try:
        if sys.version_info.minor == 6:
            return t.__extra__
        elif sys.version_info.minor == 7:
            return t.__origin__
    except AttributeError:
        return t


def type_name(t):
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
    try:
        # noinspection PyProtectedMember
        # noinspection PyUnresolvedReferences
        return t.__class__ is typing._GenericAlias
    except AttributeError:
        if sys.version_info.minor == 6:
            try:
                # noinspection PyUnresolvedReferences
                return t.__class__ == typing.GenericMeta
            except AttributeError:
                return False
        else:
            raise NotImplementedError


def is_union(t):
    try:
        return t.__origin__ is typing.Union
    except AttributeError:
        return False


class CodeBuilder:
    def __init__(self, cls):
        self.cls = cls
        self.lines = None
        self.modules = None
        self._current_indent = None

    def reset(self):
        self.lines = []
        self.modules = get_imported_module_names()
        self._current_indent = ''

    @property
    def namespace(self):
        return self.cls.__dict__

    @property
    def fields(self):
        return typing.get_type_hints(self.cls)

    @property
    def defaults(self):
        return {name: self.namespace.get(name, MISSING) for name in self.fields}

    def _add_type_modules(self, *types_):
        for t in types_:
            module = t.__module__
            if module not in self.modules:
                self.modules.add(module)
                self.add_line(f"import {module}")
                self.add_line(f"globals()['{module}'] = {module}")
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
        if not self.fields:
            return

        self.add_line('@classmethod')
        self.add_line("def from_dict(cls, d):")
        with self.indent():
            self.add_line('try:')
            with self.indent():
                self.add_line("kwargs = {}")
                for fname, ftype in self.fields.items():
                    self._add_type_modules(ftype)
                    self.add_line(f"value = d.get('{fname}', MISSING)")
                    if self.defaults[fname] is MISSING:
                        self.add_line(f"if value is MISSING:")
                        with self.indent():
                            self._add_type_modules(ftype)
                            self.add_line(f"raise MissingField('{fname}',"
                                          f"{type_name(ftype)},cls)")
                        self.add_line(f"else:")
                        with self.indent():
                            self._unpack_field_value(fname, ftype, self.cls)
                    else:
                        self.add_line("if value is not MISSING:")
                        with self.indent():
                            self._unpack_field_value(fname, ftype, self.cls)
            self.add_line('except AttributeError:')
            with self.indent():
                self.add_line('if not isinstance(d, dict):')
                with self.indent():
                    self.add_line(f"raise ValueError('Argument for "
                                  f"{type_name(self.cls)}.from_dict method "
                                  f"should be a dict instance')")
                self.add_line('else:')
                with self.indent():
                    self.add_line('raise')
            self.add_line("return cls(**kwargs)")
        self.add_line(f"setattr(cls, 'from_dict', from_dict)")
        self.compile()

    def add_to_dict(self):

        self.reset()
        if not self.fields:
            return

        self.add_line("def to_dict(self):")
        with self.indent():
            self.add_line("kwargs = {}")
            for fname, ftype in self.fields.items():
                self.add_line(f"value = getattr(self, '{fname}')")
                self._pack_field_value(fname, ftype, self.cls)
            self.add_line("return kwargs")
        self.add_line(f"setattr(cls, 'to_dict', to_dict)")
        self.compile()

    def _pack_field_value(self, fname, ftype, parent):

        is_serializable = False

        def add_fkey(expr):
            nonlocal is_serializable
            is_serializable = True
            self.add_line(f"kwargs['{fname}'] = {expr}")

        if is_dataclass(ftype):
            add_fkey(f"value.to_dict()")
            return

        pack_dataclass_gen = 'v.to_dict() for v in value'

        origin_type = get_type_origin(ftype)
        if is_special_typing_primitive(origin_type):
            # TODO: упаковывать dataclass и вложенные типы
            add_fkey('value')
        elif issubclass(origin_type, typing.Collection):
            # TODO: упаковывать вложенные типы
            args = getattr(ftype, '__args__', ())
            if issubclass(origin_type, typing.List):
                if ftype is list:
                    add_fkey('value')
                elif is_generic(ftype):
                    if is_dataclass(args[0]):
                        add_fkey(f"[{pack_dataclass_gen}]")
                    else:
                        add_fkey('[v for v in value]')
                else:
                    add_fkey('[v for v in value]')
            elif issubclass(origin_type, (typing.Deque, typing.Tuple,
                                          typing.Set, typing.FrozenSet)):
                if is_generic(ftype) and is_dataclass(args[0]):
                    add_fkey(f"[{pack_dataclass_gen}]")
                else:
                    add_fkey('[v for v in value]')
            elif issubclass(origin_type, typing.ChainMap):
                if ftype is collections.ChainMap:
                    add_fkey('value.maps')
                elif is_generic(ftype):
                    if is_dataclass(args[0]):
                        raise UnserializableDataError(
                            'ChainMaps with dataclasses as keys '
                            'are not supported by mashumaro')
                    elif is_dataclass(args[1]):
                        add_fkey('[{k: v.to_dict() for k,v in m.items()} '
                                 'for m in value.maps]')
                    else:
                        add_fkey('[m for m in value.maps]')
                else:
                    add_fkey('[m for m in value.maps]')
            elif issubclass(origin_type, typing.Mapping):
                if ftype is dict:
                    add_fkey('value')
                elif is_generic(ftype):
                    if is_dataclass(args[0]):
                        raise UnserializableDataError(
                            'Mappings with dataclasses as keys '
                            'are not supported by mashumaro')
                    elif is_dataclass(args[1]):
                        add_fkey('{k: v.to_dict() for k,v in value.items()}')
                    else:
                        add_fkey('{k: v for k,v in value.items()}')
                else:
                    add_fkey('{k: v for k,v in value.items()}')
            elif issubclass(origin_type, typing.ByteString):
                add_fkey('hexlify(value)')
            elif issubclass(origin_type, str):
                add_fkey('value')
            elif issubclass(origin_type, typing.Sequence):
                if is_generic(ftype) and is_dataclass(args[0]):
                    add_fkey(f"[{pack_dataclass_gen}]")
                else:
                    add_fkey('[v for v in value]')
            if not is_serializable:
                raise UnserializableField(fname, ftype, parent)
        else:
            add_fkey('value')

    def _unpack_field_value(self, fname, ftype, parent):

        is_serializable = False

        def add_fkey(expr):
            nonlocal is_serializable
            is_serializable = True
            self.add_line(f"kwargs['{fname}'] = {expr}")

        def unpack_dataclass_gen(arg_type):
            return f"{type_name(arg_type)}.from_dict(v) for v in value"

        if is_dataclass(ftype):
            add_fkey(f"{type_name(ftype)}.from_dict(value)")
            return

        origin_type = get_type_origin(ftype)
        if is_special_typing_primitive(origin_type):
            # TODO: распаковывать dataclass и вложенные типы
            if origin_type in (typing.Any, typing.AnyStr):
                add_fkey('value')
            elif is_union(ftype):
                # TODO: выбирать в рантайме подходящий тип
                args = getattr(ftype, '__args__', ())
                if len(args) == 2 and args[1] == NoneType:  # it is Optional
                    if is_dataclass(args[0]):
                        add_fkey(f"{type_name(args[0])}.from_dict(value)")
                    else:
                        add_fkey('value')
                else:
                    add_fkey('value')
            elif hasattr(origin_type, '__constraints__'):
                if origin_type in origin_type.__constraints__:
                    # TODO: выбирать в рантайме подходящий тип
                    add_fkey('value')
        else:
            if issubclass(origin_type, typing.Collection):
                # TODO: распаковывать вложенные типы
                args = getattr(ftype, '__args__', ())
                if issubclass(origin_type, typing.List):
                    if ftype is list:
                        add_fkey('value')
                    elif is_generic(ftype):
                        if is_dataclass(args[0]):
                            add_fkey(f"[{unpack_dataclass_gen(args[0])}]")
                        else:
                            add_fkey('value')
                    elif inspect.isabstract(origin_type):
                        add_fkey('value')
                    elif issubclass(origin_type, SerializableSequence):
                        add_fkey(f"{type_name(origin_type)}.from_sequence("
                                 f"[v for v in value])")
                elif issubclass(origin_type, typing.Deque):
                    if ftype is collections.deque:
                        add_fkey('collections.deque(value)')
                    elif is_generic(ftype):
                        if is_dataclass(args[0]):
                            add_fkey(f"collections.deque("
                                     f"{unpack_dataclass_gen(args[0])})")
                        else:
                            add_fkey('collections.deque(value)')
                    elif inspect.isabstract(origin_type):
                        add_fkey('collections.deque(value)')
                    elif issubclass(origin_type, SerializableSequence):
                        add_fkey(f"{type_name(origin_type)}.from_sequence("
                                 f"[v for v in value])")
                elif issubclass(origin_type, typing.Tuple):
                    if ftype in (tuple, typing.Tuple):
                        add_fkey('tuple(value)')
                    elif is_generic(ftype):
                        if is_dataclass(args[0]):
                            add_fkey(f"tuple({unpack_dataclass_gen(args[0])})")
                        else:
                            add_fkey('tuple(value)')
                    elif inspect.isabstract(origin_type):
                        add_fkey('tuple(value)')
                    elif issubclass(origin_type, SerializableSequence):
                        add_fkey(f"{type_name(origin_type)}.from_sequence("
                                 f"[v for v in value])")
                elif issubclass(origin_type, typing.Set):
                    if ftype is set:
                        add_fkey('set(value)')
                    elif is_generic(ftype):
                        if is_dataclass(args[0]):
                            add_fkey(f"set({unpack_dataclass_gen(args[0])})")
                        else:
                            add_fkey('set(value)')
                    elif inspect.isabstract(origin_type):
                        add_fkey('set(value)')
                    elif issubclass(origin_type, SerializableSequence):
                        add_fkey(f"{type_name(origin_type)}.from_sequence("
                                 f"[v for v in value])")
                elif issubclass(origin_type, typing.FrozenSet):
                    if ftype is frozenset:
                        add_fkey('frozenset(value)')
                    elif is_generic(ftype):
                        if is_dataclass(args[0]):
                            add_fkey(f"frozenset("
                                     f"{unpack_dataclass_gen(args[0])})")
                        else:
                            add_fkey('frozenset(value)')
                        add_fkey('frozenset(value)')
                    elif inspect.isabstract(origin_type):
                        add_fkey('frozenset(value)')
                    elif issubclass(origin_type, SerializableSequence):
                        add_fkey(f"{type_name(origin_type)}.from_sequence("
                                 f"[v for v in value])")
                elif issubclass(origin_type, typing.ChainMap):
                    if ftype is collections.ChainMap:
                        add_fkey('collections.ChainMap(*value)')
                    elif is_generic(ftype):
                        if is_dataclass(args[0]):
                            raise UnserializableDataError(
                                'ChainMaps with dataclasses as keys '
                                'are not supported by mashumaro')
                        elif is_dataclass(args[1]):
                            dc = f"{type_name(args[1])}.from_dict(v)"
                            add_fkey(f"collections.ChainMap(*[{{k: {dc} "
                                     f"for k,v in m.items()}} for m in value])")
                        else:
                            add_fkey('collections.ChainMap(*value)')
                    elif inspect.isabstract(origin_type):
                        add_fkey('collections.ChainMap(*value)')
                    elif issubclass(origin_type, SerializableSequence):
                        add_fkey(f"{type_name(origin_type)}.from_sequence("
                                 f"[v for v in value])")
                elif issubclass(origin_type, typing.Mapping):
                    if ftype is dict:
                        add_fkey('value')
                    elif is_generic(ftype):
                        if is_dataclass(args[0]):
                            raise UnserializableDataError(
                                'Mappings with dataclasses as keys '
                                'are not supported by mashumaro')
                        elif is_dataclass(args[1]):
                            dc = f"{type_name(args[1])}.from_dict(v)"
                            add_fkey(f"{{k:{dc} for k,v in value.items()}}")
                        else:
                            add_fkey('value')
                    if inspect.isabstract(origin_type):
                        add_fkey('value')
                    elif issubclass(origin_type, SerializableMapping):
                        add_fkey(f"{type_name(origin_type)}.from_mapping("
                                 "{k: v for k, v in value.items()})")
                elif issubclass(origin_type, typing.ByteString):
                    if origin_type is bytes:
                        add_fkey('unhexlify(value)')
                    elif origin_type is bytearray:
                        add_fkey('bytearray(unhexlify(value))')
                    if inspect.isabstract(origin_type):
                        add_fkey('unhexlify(value)')
                    elif issubclass(origin_type, SerializableSequence):
                        add_fkey(f"{type_name(origin_type)}.from_sequence("
                                 f"value)")
                elif issubclass(origin_type, str):
                    if inspect.isabstract(origin_type) or origin_type is str:
                        add_fkey('value')
                elif issubclass(origin_type, typing.Sequence):
                    if inspect.isabstract(origin_type):
                        add_fkey('list(v for v in value)')
                    elif issubclass(origin_type, SerializableSequence):
                        add_fkey(f"{type_name(origin_type)}.from_sequence("
                                 f"[v for v in value])")
                if not is_serializable:
                    raise UnserializableField(fname, ftype, parent)
            else:
                add_fkey('value')
