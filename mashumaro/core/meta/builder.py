import collections
import collections.abc
import datetime
import enum
import importlib
import inspect
import ipaddress
import os
import pathlib
import sys
import types
import typing
import uuid
from base64 import decodebytes, encodebytes  # noqa
from contextlib import contextmanager, suppress

# noinspection PyProtectedMember
from dataclasses import _FIELDS, MISSING, Field, is_dataclass  # type: ignore
from decimal import Decimal
from fractions import Fraction
from functools import lru_cache
from hashlib import md5
from types import MappingProxyType

import typing_extensions

from mashumaro.config import (
    ADD_DIALECT_SUPPORT,
    TO_DICT_ADD_BY_ALIAS_FLAG,
    TO_DICT_ADD_OMIT_NONE_FLAG,
    BaseConfig,
)
from mashumaro.core.const import PY_39_MIN
from mashumaro.core.helpers import *  # noqa
from mashumaro.core.meta.helpers import (
    get_args,
    get_class_that_defines_field,
    get_class_that_defines_method,
    get_literal_values,
    get_name_error_name,
    get_type_origin,
    is_class_var,
    is_dataclass_dict_mixin,
    is_dataclass_dict_mixin_subclass,
    is_dialect_subclass,
    is_generic,
    is_init_var,
    is_literal,
    is_named_tuple,
    is_new_type,
    is_optional,
    is_special_typing_primitive,
    is_type_var,
    is_type_var_any,
    is_typed_dict,
    is_union,
    not_none_type_arg,
    resolve_type_vars,
    type_name,
)
from mashumaro.core.meta.patch import patch_fromisoformat
from mashumaro.dialect import Dialect
from mashumaro.exceptions import (  # noqa
    BadDialect,
    BadHookSignature,
    InvalidFieldValue,
    MissingField,
    ThirdPartyModuleNotFoundError,
    UnresolvedTypeReferenceError,
    UnserializableDataError,
    UnserializableField,
    UnsupportedDeserializationEngine,
    UnsupportedSerializationEngine,
)
from mashumaro.helper import pass_through
from mashumaro.types import (
    GenericSerializableType,
    SerializableType,
    SerializationStrategy,
)

if PY_39_MIN:
    import zoneinfo

try:
    import ciso8601
except ImportError:  # pragma no cover
    ciso8601: typing.Optional[types.ModuleType] = None  # type: ignore
try:
    import pendulum
except ImportError:  # pragma no cover
    pendulum: typing.Optional[types.ModuleType] = None  # type: ignore

patch_fromisoformat()


NoneType = type(None)


__PRE_SERIALIZE__ = "__pre_serialize__"
__PRE_DESERIALIZE__ = "__pre_deserialize__"
__POST_SERIALIZE__ = "__post_serialize__"
__POST_DESERIALIZE__ = "__post_deserialize__"


class CodeLines:
    def __init__(self):
        self._lines: typing.List[str] = []
        self._current_indent: str = ""

    def append(self, line: str) -> None:
        self._lines.append(f"{self._current_indent}{line}")

    @contextmanager
    def indent(self) -> typing.Generator[None, None, None]:
        self._current_indent += " " * 4
        try:
            yield
        finally:
            self._current_indent = self._current_indent[:-4]

    def as_text(self) -> str:
        return "\n".join(self._lines)

    def reset(self) -> None:
        self._lines = []
        self._current_indent = ""


class CodeBuilder:
    def __init__(
        self,
        cls,
        arg_types: typing.Tuple = (),
        dialect: typing.Optional[typing.Type[Dialect]] = None,
        first_method: str = "from_dict",
        allow_postponed_evaluation: bool = True,
    ):
        self.cls = cls
        self.lines: CodeLines = CodeLines()
        self.globals: typing.Dict[str, typing.Any] = {}
        self.type_vars: typing.Dict = {}
        self.field_classes: typing.Dict = {}
        self.initial_arg_types = arg_types
        if dialect is not None and not is_dialect_subclass(dialect):
            raise BadDialect(
                f'Keyword argument "dialect" must be a subclass of Dialect '
                f"in {type_name(self.cls)}.{first_method}"
            )
        self.dialect = dialect
        self.allow_postponed_evaluation = allow_postponed_evaluation

    def reset(self) -> None:
        self.lines.reset()
        self.globals = globals().copy()
        self.type_vars = resolve_type_vars(
            cls=self.cls,
            arg_types=self.initial_arg_types,
            is_cls_created=bool(self.initial_arg_types),
        )
        self.field_classes = {}

    @property
    def namespace(self) -> typing.Dict[typing.Any, typing.Any]:
        return self.cls.__dict__

    @property
    def annotations(self) -> typing.Dict[str, typing.Any]:
        return self.namespace.get("__annotations__", {})

    def __get_field_types(
        self, recursive=True
    ) -> typing.Dict[str, typing.Any]:
        fields = {}
        globalns = sys.modules[self.cls.__module__].__dict__.copy()
        globalns[self.cls.__name__] = self.cls
        try:
            field_type_hints = typing.get_type_hints(
                self.cls, globalns, self.cls.__dict__
            )
        except NameError as e:
            name = get_name_error_name(e)
            raise UnresolvedTypeReferenceError(self.cls, name) from None
        for fname, ftype in field_type_hints.items():
            if is_class_var(ftype) or is_init_var(ftype):
                continue
            if recursive or fname in self.annotations:
                fields[fname] = ftype
        return fields

    def _get_field_class(self, field_name) -> typing.Any:
        try:
            cls = self.field_classes[field_name]
        except KeyError:
            cls = get_class_that_defines_field(field_name, self.cls)
            self.field_classes[field_name] = cls
        return cls

    def __get_real_type(self, field_name, field_type) -> typing.Any:
        cls = self._get_field_class(field_name)
        return self.type_vars[cls].get(field_type, field_type)

    def _get_field_type_vars(self, field_name) -> typing.Dict[str, typing.Any]:
        cls = self._get_field_class(field_name)
        return self.type_vars[cls]

    @property
    def field_types(self) -> typing.Dict[str, typing.Any]:
        return self.__get_field_types()

    @property  # type: ignore
    @lru_cache()
    def dataclass_fields(self) -> typing.Dict[str, Field]:
        d = {}
        for ancestor in self.cls.__mro__[-1:0:-1]:
            if is_dataclass(ancestor):
                for field in getattr(ancestor, _FIELDS).values():
                    d[field.name] = field
        for name in self.__get_field_types(recursive=False):
            field = self.namespace.get(name, MISSING)
            if isinstance(field, Field):
                d[name] = field
            else:
                field = self.namespace.get(_FIELDS, {}).get(name, MISSING)
                if isinstance(field, Field):
                    d[name] = field
                else:
                    d.pop(name, None)
        return d

    @property
    def metadatas(self) -> typing.Dict[str, typing.Mapping[str, typing.Any]]:
        return {
            name: field.metadata
            for name, field in self.dataclass_fields.items()  # type: ignore
            # https://github.com/python/mypy/issues/1362
        }

    def get_field_default(self, name: str) -> typing.Any:
        field = self.dataclass_fields.get(name)  # type: ignore
        # https://github.com/python/mypy/issues/1362
        if field:
            if field.default is not MISSING:
                return field.default
            else:
                return field.default_factory
        else:
            return self.namespace.get(name, MISSING)

    def _add_type_modules(self, *types_) -> None:
        for t in types_:
            module = inspect.getmodule(t)
            if not module:
                continue
            self.ensure_module_imported(module)
            if is_literal(t):
                args = get_literal_values(t)
                self._add_type_modules(*args)
            else:
                args = get_args(t)
                if args:
                    self._add_type_modules(*args)
            constraints = getattr(t, "__constraints__", ())
            if constraints:
                self._add_type_modules(*constraints)
            bound = getattr(t, "__bound__", ())
            if bound:
                self._add_type_modules(bound)

    def ensure_module_imported(self, module: types.ModuleType) -> None:
        self.globals.setdefault(module.__name__, module)
        package = module.__name__.split(".")[0]
        self.globals.setdefault(package, importlib.import_module(package))

    def add_line(self, line: str) -> None:
        self.lines.append(line)

    @contextmanager
    def indent(self) -> typing.Generator[None, None, None]:
        with self.lines.indent():
            yield

    def compile(self) -> None:
        code = self.lines.as_text()
        if self.get_config().debug:
            if self.dialect is not None:
                print(f"{type_name(self.cls)}[{type_name(self.dialect)}]:")
            else:
                print(f"{type_name(self.cls)}:")
            print(code)
        exec(code, self.globals, self.__dict__)

    def get_declared_hook(self, method_name: str) -> typing.Any:
        if not hasattr(self.cls, method_name):
            return
        cls = get_class_that_defines_method(method_name, self.cls)
        if not is_dataclass_dict_mixin(cls):
            return cls.__dict__[method_name]

    def _add_from_dict(self) -> None:
        method_name = "from_dict"
        if self.initial_arg_types:
            method_name += f"_{self._hash_arg_types(self.initial_arg_types)}"
        if self.dialect is None:
            self.add_line("@classmethod")
        default_kwargs = self.get_from_dict_default_flag_values()
        if default_kwargs:
            self.add_line(f"def {method_name}(cls, d, {default_kwargs}):")
        else:
            self.add_line(f"def {method_name}(cls, d):")
        with self.indent():
            self._add_from_dict_lines()
        if self.dialect is None:
            self.add_line(f"setattr(cls, '{method_name}', {method_name})")
        else:
            self.add_line(
                f"cls.__dialect_from_dict_cache__[dialect] = {method_name}"
            )
        self.compile()

    def _add_from_dict_lines(self) -> None:
        config = self.get_config()
        try:
            field_types = self.field_types
        except UnresolvedTypeReferenceError:
            if (
                not self.allow_postponed_evaluation
                or not config.allow_postponed_evaluation
            ):
                raise
            self.add_line(
                "builder = CodeBuilder(cls, allow_postponed_evaluation=False)"
            )
            self.add_line("builder.add_from_dict()")
            from_dict_args = ", ".join(
                filter(None, ("d", self.get_from_dict_flags()))
            )
            self.add_line(f"return cls.from_dict({from_dict_args})")
        else:
            pre_deserialize = self.get_declared_hook(__PRE_DESERIALIZE__)
            if pre_deserialize:
                if not isinstance(pre_deserialize, classmethod):
                    raise BadHookSignature(
                        f"`{__PRE_DESERIALIZE__}` must be a class method with "
                        f"Callable[[Dict[Any, Any]], Dict[Any, Any]] signature"
                    )
                else:
                    self.add_line(f"d = cls.{__PRE_DESERIALIZE__}(d)")
            self.add_line("try:")
            with self.indent():
                self.add_line("kwargs = {}")
                for fname, ftype in field_types.items():
                    self._add_type_modules(ftype)
                    metadata = self.metadatas.get(fname, {})
                    alias = metadata.get("alias")
                    if alias is None:
                        alias = config.aliases.get(fname)
                    self._from_dict_set_value(fname, ftype, metadata, alias)
            self.add_line("except AttributeError:")
            with self.indent():
                self.add_line("if not isinstance(d, dict):")
                with self.indent():
                    self.add_line(
                        f"raise ValueError('Argument for "
                        f"{type_name(self.cls)}.from_dict method "
                        f"should be a dict instance') from None"
                    )
                self.add_line("else:")
                with self.indent():
                    self.add_line("raise")
            post_deserialize = self.get_declared_hook(__POST_DESERIALIZE__)
            if post_deserialize:
                if not isinstance(post_deserialize, classmethod):
                    raise BadHookSignature(
                        f"`{__POST_DESERIALIZE__}` must be a class method "
                        f"with Callable[[{type_name(self.cls)}], "
                        f"{type_name(self.cls)}] signature"
                    )
                else:
                    self.add_line(
                        f"return cls.{__POST_DESERIALIZE__}(cls(**kwargs))"
                    )
            else:
                self.add_line("return cls(**kwargs)")

    def _add_from_dict_with_dialect_lines(self) -> None:
        from_dict_args = ", ".join(
            filter(None, ("cls", "d", self.get_from_dict_flags()))
        )
        self.add_line(
            "from_dict = cls.__dialect_from_dict_cache__.get(dialect)"
        )
        self.add_line("if from_dict is not None:")
        with self.indent():
            self.add_line(f"return from_dict({from_dict_args})")
        self.add_line(
            "CodeBuilder(cls,dialect=dialect,"
            "first_method='from_dict').add_from_dict()"
        )
        self.add_line(
            f"return cls.__dialect_from_dict_cache__[dialect]"
            f"({from_dict_args})"
        )

    def add_from_dict(self) -> None:
        self.reset()
        dialects_feature = self.is_code_generation_option_enabled(
            ADD_DIALECT_SUPPORT
        )
        if dialects_feature:
            self.add_line(
                "if not hasattr(cls, '__dialect_from_dict_cache__'):"
            )
            with self.indent():
                self.add_line("cls.__dialect_from_dict_cache__ = {}")
        if not dialects_feature or dialects_feature and self.dialect:
            return self._add_from_dict()

        method_name = "from_dict"
        if self.initial_arg_types:
            method_name += f"_{self._hash_arg_types(self.initial_arg_types)}"
        self.add_line("@classmethod")
        default_kwargs = self.get_from_dict_default_flag_values()
        if default_kwargs:
            self.add_line(f"def {method_name}(cls, d, {default_kwargs}):")
        else:  # pragma no cover
            # there will be at least a dialect parameter
            self.add_line(f"def {method_name}(cls, d):")
        with self.indent():
            self.add_line("if dialect is None:")
            with self.indent():
                self._add_from_dict_lines()
            self.add_line("else:")
            with self.indent():
                self._add_from_dict_with_dialect_lines()
        self.add_line(f"setattr(cls, '{method_name}', {method_name})")
        self.compile()

    def _from_dict_set_value(self, fname, ftype, metadata, alias=None) -> None:
        unpacked_value = self._unpack_field_value(
            fname=fname,
            ftype=ftype,
            parent=self.cls,
            metadata=metadata,
        )
        self.add_line(f"value = d.get('{alias or fname}', MISSING)")
        self.add_line("if value is None:")
        with self.indent():
            self.add_line(f"kwargs['{fname}'] = None")
        if self.get_field_default(fname) is MISSING:
            self.add_line("elif value is MISSING:")
            with self.indent():
                field_type = type_name(
                    ftype, type_vars=self._get_field_type_vars(fname)
                )
                self.add_line(
                    f"raise MissingField('{fname}'," f"{field_type},cls)"
                )
            self.add_line("else:")
            with self.indent():
                if unpacked_value == "value":
                    self.add_line(f"kwargs['{fname}'] = {unpacked_value}")
                else:
                    self.add_line("try:")
                    with self.indent():
                        self.add_line(f"kwargs['{fname}'] = {unpacked_value}")
                    self.add_line("except Exception as e:")
                    with self.indent():
                        field_type = type_name(
                            ftype, type_vars=self._get_field_type_vars(fname)
                        )
                        self.add_line(
                            f"raise InvalidFieldValue('{fname}',"
                            f"{field_type},value,cls)"
                        )
        else:
            self.add_line("elif value is not MISSING:")
            with self.indent():
                if unpacked_value == "value":
                    self.add_line(f"kwargs['{fname}'] = {unpacked_value}")
                else:
                    self.add_line("try:")
                    with self.indent():
                        self.add_line(f"kwargs['{fname}'] = {unpacked_value}")
                    self.add_line("except Exception as e:")
                    with self.indent():
                        field_type = type_name(
                            ftype, type_vars=self._get_field_type_vars(fname)
                        )
                        self.add_line(
                            f"raise InvalidFieldValue('{fname}',"
                            f"{field_type},value,cls)"
                        )

    @lru_cache()
    def get_config(self, cls=None) -> typing.Type[BaseConfig]:
        if cls is None:
            cls = self.cls
        config_cls = getattr(cls, "Config", BaseConfig)
        if not issubclass(config_cls, BaseConfig):
            config_cls = type(
                "Config",
                (BaseConfig, config_cls),
                {**BaseConfig.__dict__, **config_cls.__dict__},
            )
        return config_cls

    def get_to_dict_flags(self, cls=None) -> str:
        pluggable_flags = []
        for option, flag in (
            (TO_DICT_ADD_OMIT_NONE_FLAG, "omit_none"),
            (TO_DICT_ADD_BY_ALIAS_FLAG, "by_alias"),
            (ADD_DIALECT_SUPPORT, "dialect"),
        ):
            if self.is_code_generation_option_enabled(option, cls):
                if self.is_code_generation_option_enabled(option):
                    pluggable_flags.append(f"{flag}={flag}")
        return ", ".join(pluggable_flags)

    def get_from_dict_flags(self, cls=None) -> str:
        pluggable_flags = []
        for option, flag in ((ADD_DIALECT_SUPPORT, "dialect"),):
            if self.is_code_generation_option_enabled(option, cls):
                if self.is_code_generation_option_enabled(option):
                    pluggable_flags.append(f"{flag}={flag}")
        return ", ".join(pluggable_flags)

    def get_to_dict_default_flag_values(self, cls=None) -> str:
        flag_names = []
        flag_values = []
        omit_none_feature = self.is_code_generation_option_enabled(
            TO_DICT_ADD_OMIT_NONE_FLAG, cls
        )
        if omit_none_feature:
            flag_names.append("omit_none")
            flag_values.append("False")
        by_alias_feature = self.is_code_generation_option_enabled(
            TO_DICT_ADD_BY_ALIAS_FLAG, cls
        )
        if by_alias_feature:
            serialize_by_alias = self.get_config(cls).serialize_by_alias
            flag_names.append("by_alias")
            flag_values.append("True" if serialize_by_alias else "False")
        dialects_feature = self.is_code_generation_option_enabled(
            ADD_DIALECT_SUPPORT, cls
        )
        if dialects_feature:
            flag_names.append("dialect")
            flag_values.append("None")
        if flag_names:
            pluggable_flags_str = "*, " + ", ".join(
                [f"{n}={v}" for n, v in zip(flag_names, flag_values)]
            )
        else:
            pluggable_flags_str = ""
        return pluggable_flags_str

    def get_from_dict_default_flag_values(self, cls=None) -> str:
        flag_names = []
        flag_values = []
        dialects_feature = self.is_code_generation_option_enabled(
            ADD_DIALECT_SUPPORT, cls
        )
        if dialects_feature:
            flag_names.append("dialect")
            flag_values.append("None")
        if flag_names:
            pluggable_flags_str = "*, " + ", ".join(
                [f"{n}={v}" for n, v in zip(flag_names, flag_values)]
            )
        else:
            pluggable_flags_str = ""
        return pluggable_flags_str

    def is_code_generation_option_enabled(self, option: str, cls=None) -> bool:
        if option == ADD_DIALECT_SUPPORT:
            # TODO: make inheritance for code_generation_options
            for ancestor in self.cls.__mro__[-1:0:-1]:
                if (
                    type_name(ancestor)
                    == "mashumaro.mixins.msgpack.DataClassMessagePackMixin"
                ):
                    return True
        return option in self.get_config(cls).code_generation_options

    def _add_to_dict(self) -> None:
        method_name = "to_dict"
        if self.initial_arg_types:
            method_name += f"_{self._hash_arg_types(self.initial_arg_types)}"
        self.reset()
        default_kwargs = self.get_to_dict_default_flag_values()
        if default_kwargs:
            self.add_line(f"def {method_name}(self, {default_kwargs}):")
        else:
            self.add_line(f"def {method_name}(self):")
        with self.indent():
            self._add_to_dict_lines()
        if self.dialect is None:
            self.add_line(f"setattr(cls, '{method_name}', {method_name})")
        else:
            self.add_line(
                f"cls.__dialect_to_dict_cache__[dialect] = {method_name}"
            )
        self.compile()

    def _add_to_dict_lines(self) -> None:
        config = self.get_config()
        try:
            field_types = self.field_types
        except UnresolvedTypeReferenceError:
            if (
                not self.allow_postponed_evaluation
                or not config.allow_postponed_evaluation
            ):
                raise
            self.add_line(
                "builder = CodeBuilder(self.__class__, "
                "allow_postponed_evaluation=False)"
            )
            self.add_line("builder.add_to_dict()")
            self.add_line(f"return self.to_dict({self.get_to_dict_flags()})")
        else:
            pre_serialize = self.get_declared_hook(__PRE_SERIALIZE__)
            if pre_serialize:
                self.add_line(f"self = self.{__PRE_SERIALIZE__}()")
            self.add_line("kwargs = {}")
            for fname, ftype in field_types.items():
                metadata = self.metadatas.get(fname, {})
                self._to_dict_set_value(fname, ftype, metadata)
            post_serialize = self.get_declared_hook(__POST_SERIALIZE__)
            if post_serialize:
                self.add_line(f"return self.{__POST_SERIALIZE__}(kwargs)")
            else:
                self.add_line("return kwargs")

    def _add_to_dict_with_dialect_lines(self) -> None:
        to_dict_args = ", ".join(
            filter(None, ("self", self.get_to_dict_flags()))
        )
        self.add_line(
            "to_dict = self.__class__."
            "__dialect_to_dict_cache__.get(dialect)"
        )
        self.add_line("if to_dict is not None:")
        with self.indent():
            self.add_line(f"return to_dict({to_dict_args})")
        self.add_line(
            "CodeBuilder(self.__class__,dialect=dialect,"
            "first_method='to_dict').add_to_dict()"
        )
        self.add_line(
            f"return self.__class__.__dialect_to_dict_cache__[dialect]"
            f"({to_dict_args})"
        )

    def add_to_dict(self) -> None:
        self.reset()
        dialects_feature = self.is_code_generation_option_enabled(
            ADD_DIALECT_SUPPORT
        )
        if dialects_feature:
            self.add_line("if not hasattr(cls, '__dialect_to_dict_cache__'):")
            with self.indent():
                self.add_line("cls.__dialect_to_dict_cache__ = {}")
        if not dialects_feature or dialects_feature and self.dialect:
            return self._add_to_dict()

        method_name = "to_dict"
        if self.initial_arg_types:
            method_name += f"_{self._hash_arg_types(self.initial_arg_types)}"
        default_kwargs = self.get_to_dict_default_flag_values()
        if default_kwargs:
            self.add_line(f"def {method_name}(self, {default_kwargs}):")
        else:  # pragma no cover
            # there will be at least a dialect parameter
            self.add_line(f"def {method_name}(self):")
        with self.indent():
            self.add_line("if dialect is None:")
            with self.indent():
                self._add_to_dict_lines()
            self.add_line("else:")
            with self.indent():
                self._add_to_dict_with_dialect_lines()
        self.add_line(f"setattr(cls, '{method_name}', {method_name})")
        self.compile()

    def _to_dict_set_value(self, fname, ftype, metadata) -> None:
        omit_none_feature = self.is_code_generation_option_enabled(
            TO_DICT_ADD_OMIT_NONE_FLAG
        )
        by_alias_feature = self.is_code_generation_option_enabled(
            TO_DICT_ADD_BY_ALIAS_FLAG
        )
        config = self.get_config()
        alias = metadata.get("alias")
        if alias is None:
            alias = config.aliases.get(fname)
        serialize_by_alias = self.get_config().serialize_by_alias
        if serialize_by_alias and alias is not None:
            fname_or_alias = alias
        else:
            fname_or_alias = fname

        self.add_line(f"value = getattr(self, '{fname}')")
        self.add_line("if value is None:")
        with self.indent():
            if omit_none_feature:
                self.add_line("if not omit_none:")
                with self.indent():
                    if by_alias_feature and alias is not None:
                        self.add_line("if by_alias:")
                        with self.indent():
                            self.add_line(f"kwargs['{alias}'] = None")
                        self.add_line("else:")
                        with self.indent():
                            self.add_line(f"kwargs['{fname}'] = None")
                    else:
                        self.add_line(f"kwargs['{fname_or_alias}'] = None")
            else:
                if by_alias_feature and alias is not None:
                    self.add_line("if by_alias:")
                    with self.indent():
                        self.add_line(f"kwargs['{alias}'] = None")
                    self.add_line("else:")
                    with self.indent():
                        self.add_line(f"kwargs['{fname}'] = None")
                else:
                    self.add_line(f"kwargs['{fname_or_alias}'] = None")
        self.add_line("else:")
        with self.indent():
            packed_value = self._pack_value(
                fname=fname,
                ftype=ftype,
                parent=self.cls,
                metadata=metadata,
            )
            if by_alias_feature and alias is not None:
                self.add_line("if by_alias:")
                with self.indent():
                    self.add_line(f"kwargs['{alias}'] = {packed_value}")
                self.add_line("else:")
                with self.indent():
                    self.add_line(f"kwargs['{fname}'] = {packed_value}")
            else:
                self.add_line(f"kwargs['{fname_or_alias}'] = {packed_value}")

    def _pack_value(
        self,
        fname,
        ftype,
        parent,
        value_name="value",
        metadata=MappingProxyType({}),
        could_be_none=False,
    ):

        ftype = self.__get_real_type(fname, ftype)
        origin_type = get_type_origin(ftype)

        strategy: typing.Optional[SerializationStrategy] = None
        serialize_option = metadata.get("serialize")
        overridden_fn_suffix = str(uuid.uuid4().hex)
        if serialize_option is None:
            strategy = metadata.get("serialization_strategy")
            if isinstance(strategy, SerializationStrategy):
                serialize_option = strategy.serialize
        if serialize_option is None:
            if self.dialect is not None:
                strategy = self.dialect.serialization_strategy.get(ftype)
                if isinstance(strategy, dict):
                    serialize_option = strategy.get("serialize")
                elif isinstance(strategy, SerializationStrategy):
                    serialize_option = strategy.serialize
        if serialize_option is None:
            default_dialect = self.get_config().dialect
            if default_dialect is not None:
                if not is_dialect_subclass(default_dialect):
                    raise BadDialect(
                        f'Config option "dialect" of '
                        f"{type_name(self.cls)} must be a subclass of Dialect"
                    )
                strategy = default_dialect.serialization_strategy.get(ftype)
                if isinstance(strategy, dict):
                    serialize_option = strategy.get("serialize")
                elif isinstance(strategy, SerializationStrategy):
                    serialize_option = strategy.serialize
        if serialize_option is None:
            strategy = self.get_config().serialization_strategy.get(ftype)
            if isinstance(strategy, dict):
                serialize_option = strategy.get("serialize")
            elif isinstance(strategy, SerializationStrategy):
                serialize_option = strategy.serialize
        if pass_through in (strategy, serialize_option):
            return value_name
        elif callable(serialize_option):
            overridden_fn = f"__{fname}_serialize_{overridden_fn_suffix}"
            setattr(self.cls, overridden_fn, staticmethod(serialize_option))
            return f"self.{overridden_fn}({value_name})"

        with suppress(TypeError):
            if issubclass(origin_type, SerializableType):
                return f"{value_name}._serialize()"
        with suppress(TypeError):
            if issubclass(origin_type, GenericSerializableType):
                arg_type_names = ", ".join(
                    list(map(type_name, get_args(ftype)))
                )
                return f"{value_name}._serialize([{arg_type_names}])"

        if is_dataclass_dict_mixin_subclass(origin_type):
            arg_types = get_args(ftype)
            if arg_types:
                method_name = f"to_dict_{self._hash_arg_types(arg_types)}"
                if not hasattr(origin_type, method_name):  # pragma no cover
                    builder = CodeBuilder(origin_type, arg_types)
                    builder.add_from_dict()
                    builder.add_to_dict()
            else:
                method_name = "to_dict"
            flags = self.get_to_dict_flags(ftype)
            return f"{value_name}.{method_name}({flags})"

        if is_special_typing_primitive(origin_type):
            if origin_type is typing.Any:
                return value_name
            elif is_union(ftype):
                args = get_args(ftype)
                field_type_vars = self._get_field_type_vars(fname)
                if is_optional(ftype, field_type_vars):
                    arg = not_none_type_arg(args, field_type_vars)
                    pv = self._pack_value(
                        fname, arg, parent, value_name, metadata=metadata
                    )
                    if could_be_none:
                        return f"{pv} if {value_name} is not None else None"
                    else:
                        return pv
                else:
                    return self._pack_union(
                        fname, ftype, value_name, args, parent, metadata
                    )
            elif origin_type is typing.AnyStr:
                raise UnserializableDataError(
                    "AnyStr is not supported by mashumaro"
                )
            elif is_type_var_any(ftype):
                return value_name
            elif is_type_var(ftype):
                constraints = getattr(ftype, "__constraints__")
                if constraints:
                    return self._pack_union(
                        fname=fname,
                        ftype=ftype,
                        value_name=value_name,
                        args=constraints,
                        parent=parent,
                        metadata=metadata,
                        prefix="type_var",
                    )
                else:
                    bound = getattr(ftype, "__bound__")
                    # act as if it was Optional[bound]
                    pv = self._pack_value(
                        fname, bound, parent, value_name, metadata
                    )
                    if could_be_none:
                        return f"{pv} if {value_name} is not None else None"
                    else:
                        return pv
            elif is_new_type(ftype):
                return self._pack_value(
                    fname=fname,
                    ftype=ftype.__supertype__,
                    parent=parent,
                    value_name=value_name,
                    metadata=metadata,
                    could_be_none=could_be_none,
                )
            elif is_literal(ftype):
                return self._pack_literal(
                    fname, ftype, value_name, parent, metadata
                )
            else:
                raise UnserializableDataError(
                    f"{ftype} as a field type is not supported by mashumaro"
                )
        elif origin_type is int:
            return f"int({value_name})"
        elif origin_type is float:
            return f"float({value_name})"
        elif origin_type in (bool, NoneType, None):
            return value_name
        elif origin_type in (datetime.datetime, datetime.date, datetime.time):
            return f"{value_name}.isoformat()"
        elif origin_type is datetime.timedelta:
            return f"{value_name}.total_seconds()"
        elif origin_type is datetime.timezone:
            return f"{value_name}.tzname(None)"
        elif PY_39_MIN and origin_type is zoneinfo.ZoneInfo:
            return f"str({value_name})"
        elif origin_type is uuid.UUID:
            return f"str({value_name})"
        elif origin_type in [
            ipaddress.IPv4Address,
            ipaddress.IPv6Address,
            ipaddress.IPv4Network,
            ipaddress.IPv6Network,
            ipaddress.IPv4Interface,
            ipaddress.IPv6Interface,
        ]:
            return f"str({value_name})"
        elif origin_type is Decimal:
            return f"str({value_name})"
        elif origin_type is Fraction:
            return f"str({value_name})"
        elif issubclass(origin_type, typing.Collection) and not issubclass(
            origin_type, enum.Enum
        ):
            args = get_args(ftype)

            def inner_expr(arg_num=0, v_name="value", v_type=None):
                if v_type:
                    return self._pack_value(fname, v_type, parent, v_name)
                else:
                    if args and len(args) > arg_num:
                        arg_type = args[arg_num]
                    else:
                        arg_type = typing.Any
                    return self._pack_value(
                        fname, arg_type, parent, v_name, could_be_none=True
                    )

            if issubclass(origin_type, typing.ByteString):
                return f"encodebytes({value_name}).decode()"
            elif issubclass(origin_type, str):
                return value_name
            elif issubclass(origin_type, typing.Tuple):
                if is_named_tuple(ftype):
                    return self._pack_named_tuple(
                        fname,
                        ftype,
                        value_name,
                        parent,
                        metadata,
                        serialize_option,
                    )
                elif is_generic(ftype):
                    return self._pack_tuple(
                        fname, value_name, args, parent, metadata
                    )
                elif ftype is tuple:
                    raise UnserializableField(
                        fname, ftype, parent, "Use typing.Tuple[T] instead"
                    )
            elif issubclass(
                origin_type, (typing.List, typing.Deque, typing.AbstractSet)
            ):
                if is_generic(ftype):
                    return f"[{inner_expr()} for value in {value_name}]"
                elif ftype is list:
                    raise UnserializableField(
                        fname, ftype, parent, "Use typing.List[T] instead"
                    )
                elif ftype is collections.deque:
                    raise UnserializableField(
                        fname, ftype, parent, "Use typing.Deque[T] instead"
                    )
                elif ftype is set:
                    raise UnserializableField(
                        fname, ftype, parent, "Use typing.Set[T] instead"
                    )
                elif ftype is frozenset:
                    raise UnserializableField(
                        fname, ftype, parent, "Use typing.FrozenSet[T] instead"
                    )
            elif issubclass(origin_type, typing.ChainMap):
                if is_generic(ftype):
                    if args and is_dataclass(args[0]):
                        raise UnserializableDataError(
                            "ChainMaps with dataclasses as keys "
                            "are not supported by mashumaro"
                        )
                    else:
                        return (
                            f'[{{{inner_expr(0,"key")}:{inner_expr(1)} '
                            f"for key,value in m.items()}} "
                            f"for m in {value_name}.maps]"
                        )
                elif ftype is collections.ChainMap:
                    raise UnserializableField(
                        fname,
                        ftype,
                        parent,
                        "Use typing.ChainMap[KT,VT] instead",
                    )
            elif issubclass(origin_type, typing_extensions.OrderedDict):
                if is_generic(ftype):
                    if args and is_dataclass(args[0]):
                        raise UnserializableDataError(
                            "OrderedDict with dataclasses as keys "
                            "are not supported by mashumaro"
                        )
                    else:
                        return (
                            f'{{{inner_expr(0, "key")}: {inner_expr(1)} '
                            f"for key, value in {value_name}.items()}}"
                        )
                elif ftype is collections.OrderedDict:
                    raise UnserializableField(
                        fname,
                        ftype,
                        parent,
                        "Use typing.OrderedDict[KT,VT] instead",
                    )
            elif issubclass(origin_type, typing.Counter):
                if is_generic(ftype):
                    if args and is_dataclass(args[0]):
                        raise UnserializableDataError(
                            "Counter with dataclasses as keys "
                            "are not supported by mashumaro"
                        )
                    else:
                        return (
                            f'{{{inner_expr(0, "key")}: '
                            f"{inner_expr(1, v_type=int)} "
                            f"for key, value in {value_name}.items()}}"
                        )
                elif ftype is collections.Counter:
                    raise UnserializableField(
                        fname,
                        ftype,
                        parent,
                        "Use typing.Counter[KT] instead",
                    )
            elif issubclass(origin_type, typing.Mapping):
                if is_typed_dict(ftype):
                    return self._pack_typed_dict(
                        fname, ftype, value_name, parent, metadata
                    )
                elif is_generic(ftype):
                    if args and is_dataclass(args[0]):
                        raise UnserializableDataError(
                            "Mappings with dataclasses as keys "
                            "are not supported by mashumaro"
                        )
                    else:
                        return (
                            f'{{{inner_expr(0,"key")}: {inner_expr(1)} '
                            f"for key, value in {value_name}.items()}}"
                        )
                elif ftype is dict:
                    raise UnserializableField(
                        fname,
                        ftype,
                        parent,
                        "Use typing.Dict[KT,VT] or Mapping[KT,VT] instead",
                    )
            elif issubclass(origin_type, typing.Sequence):
                if is_generic(ftype):
                    return f"[{inner_expr()} for value in {value_name}]"
        elif issubclass(origin_type, os.PathLike):
            return f"{value_name}.__fspath__()"
        elif issubclass(origin_type, enum.Enum):
            return f"{value_name}.value"

        raise UnserializableField(fname, ftype, parent)

    def _unpack_field_value(
        self,
        fname,
        ftype,
        parent,
        value_name="value",
        metadata=MappingProxyType({}),
        could_be_none=False,
    ):

        ftype = self.__get_real_type(fname, ftype)
        origin_type = get_type_origin(ftype)

        strategy: typing.Optional[SerializationStrategy] = None
        deserialize_option = metadata.get("deserialize")
        overridden_fn_suffix = str(uuid.uuid4().hex)
        if deserialize_option is None:
            strategy = metadata.get("serialization_strategy")
            if isinstance(strategy, SerializationStrategy):
                deserialize_option = strategy.deserialize
        if deserialize_option is None:
            if self.dialect is not None:
                strategy = self.dialect.serialization_strategy.get(ftype)
                if isinstance(strategy, dict):
                    deserialize_option = strategy.get("deserialize")
                elif isinstance(strategy, SerializationStrategy):
                    deserialize_option = strategy.deserialize
        if deserialize_option is None:
            default_dialect = self.get_config().dialect
            if default_dialect is not None:
                if not is_dialect_subclass(default_dialect):
                    raise BadDialect(
                        f'Config option "dialect" of '
                        f"{type_name(self.cls)} must be a subclass of Dialect"
                    )
                strategy = default_dialect.serialization_strategy.get(ftype)
                if isinstance(strategy, dict):
                    deserialize_option = strategy.get("deserialize")
                elif isinstance(strategy, SerializationStrategy):
                    deserialize_option = strategy.deserialize
        if deserialize_option is None:
            strategy = self.get_config().serialization_strategy.get(ftype)
            if isinstance(strategy, dict):
                deserialize_option = strategy.get("deserialize")
            elif isinstance(strategy, SerializationStrategy):
                deserialize_option = strategy.deserialize
        if pass_through in (strategy, deserialize_option):
            return value_name
        elif callable(deserialize_option):
            overridden_fn = f"__{fname}_deserialize_{overridden_fn_suffix}"
            setattr(self.cls, overridden_fn, deserialize_option)
            return f"cls.{overridden_fn}({value_name})"

        with suppress(TypeError):
            if issubclass(origin_type, SerializableType):
                return f"{type_name(ftype)}._deserialize({value_name})"
        with suppress(TypeError):
            if issubclass(origin_type, GenericSerializableType):
                arg_type_names = ", ".join(
                    list(map(type_name, get_args(ftype)))
                )
                return (
                    f"{type_name(ftype)}._deserialize({value_name}, "
                    f"[{arg_type_names}])"
                )

        if is_dataclass_dict_mixin_subclass(origin_type):
            arg_types = get_args(ftype)
            if arg_types:
                method_name = f"from_dict_{self._hash_arg_types(arg_types)}"
                if not hasattr(origin_type, method_name):
                    builder = CodeBuilder(origin_type, arg_types)
                    builder.add_from_dict()
                    builder.add_to_dict()
            else:
                method_name = "from_dict"
            method_args = ", ".join(
                filter(None, (value_name, self.get_from_dict_flags(ftype)))
            )
            return f"{type_name(origin_type)}.{method_name}({method_args})"

        if is_special_typing_primitive(origin_type):
            if origin_type is typing.Any:
                return value_name
            elif is_union(ftype):
                args = get_args(ftype)
                field_type_vars = self._get_field_type_vars(fname)
                if is_optional(ftype, field_type_vars):
                    arg = not_none_type_arg(args, field_type_vars)
                    ufv = self._unpack_field_value(
                        fname, arg, parent, value_name, metadata=metadata
                    )
                    if could_be_none:
                        return f"{ufv} if {value_name} is not None else None"
                    else:
                        return ufv
                else:
                    return self._unpack_union(
                        fname, ftype, value_name, args, parent, metadata
                    )
            elif origin_type is typing.AnyStr:
                raise UnserializableDataError(
                    "AnyStr is not supported by mashumaro"
                )
            elif is_type_var_any(ftype):
                return value_name
            elif is_type_var(ftype):
                constraints = getattr(ftype, "__constraints__")
                if constraints:
                    return self._unpack_union(
                        fname=fname,
                        ftype=ftype,
                        value_name=value_name,
                        args=constraints,
                        parent=parent,
                        metadata=metadata,
                        prefix="type_var",
                    )
                else:
                    bound = getattr(ftype, "__bound__")
                    # act as if it was Optional[bound]
                    ufv = self._unpack_field_value(
                        fname, bound, parent, value_name, metadata
                    )
                    if could_be_none:
                        return f"{ufv} if {value_name} is not None else None"
                    else:
                        return ufv
            elif is_new_type(ftype):
                return self._unpack_field_value(
                    fname=fname,
                    ftype=ftype.__supertype__,
                    parent=parent,
                    value_name=value_name,
                    metadata=metadata,
                    could_be_none=could_be_none,
                )
            elif is_literal(ftype):
                return self._unpack_literal(
                    fname, ftype, value_name, parent, metadata
                )
            else:
                raise UnserializableDataError(
                    f"{ftype} as a field type is not supported by mashumaro"
                )
        elif origin_type is int:
            return f"int({value_name})"
        elif origin_type is float:
            return f"float({value_name})"
        elif origin_type in (bool, NoneType, None):
            return value_name
        elif origin_type in (datetime.datetime, datetime.date, datetime.time):
            if deserialize_option is not None:
                if deserialize_option == "ciso8601":
                    if ciso8601:
                        self.ensure_module_imported(ciso8601)
                        datetime_parser = "ciso8601.parse_datetime"
                    else:
                        raise ThirdPartyModuleNotFoundError(
                            "ciso8601", fname, parent
                        )  # pragma no cover
                elif deserialize_option == "pendulum":
                    if pendulum:
                        self.ensure_module_imported(pendulum)
                        datetime_parser = "pendulum.parse"
                    else:
                        raise ThirdPartyModuleNotFoundError(
                            "pendulum", fname, parent
                        )  # pragma no cover
                else:
                    raise UnsupportedDeserializationEngine(
                        fname, ftype, parent, deserialize_option
                    )
                suffix = ""
                if origin_type is datetime.date:
                    suffix = ".date()"
                elif origin_type is datetime.time:
                    suffix = ".time()"
                return f"{datetime_parser}({value_name}){suffix}"
            return (
                f"datetime.{origin_type.__name__}.fromisoformat({value_name})"
            )
        elif origin_type is datetime.timedelta:
            return f"datetime.timedelta(seconds={value_name})"
        elif origin_type is datetime.timezone:
            return f"parse_timezone({value_name})"
        elif PY_39_MIN and origin_type is zoneinfo.ZoneInfo:
            return f"zoneinfo.ZoneInfo({value_name})"
        elif origin_type is uuid.UUID:
            return f"uuid.UUID({value_name})"
        elif origin_type is ipaddress.IPv4Address:
            return f"ipaddress.IPv4Address({value_name})"
        elif origin_type is ipaddress.IPv6Address:
            return f"ipaddress.IPv6Address({value_name})"
        elif origin_type is ipaddress.IPv4Network:
            return f"ipaddress.IPv4Network({value_name})"
        elif origin_type is ipaddress.IPv6Network:
            return f"ipaddress.IPv6Network({value_name})"
        elif origin_type is ipaddress.IPv4Interface:
            return f"ipaddress.IPv4Interface({value_name})"
        elif origin_type is ipaddress.IPv6Interface:
            return f"ipaddress.IPv6Interface({value_name})"
        elif origin_type is Decimal:
            return f"Decimal({value_name})"
        elif origin_type is Fraction:
            return f"Fraction({value_name})"
        elif issubclass(origin_type, typing.Collection) and not issubclass(
            origin_type, enum.Enum
        ):
            args = get_args(ftype)

            def inner_expr(arg_num=0, v_name="value", v_type=None):
                if v_type:
                    return self._unpack_field_value(
                        fname, v_type, parent, v_name
                    )
                else:
                    if args and len(args) > arg_num:
                        arg_type = args[arg_num]
                    else:
                        arg_type = typing.Any
                    return self._unpack_field_value(
                        fname, arg_type, parent, v_name, could_be_none=True
                    )

            if issubclass(origin_type, typing.ByteString):
                if origin_type is bytes:
                    return f"decodebytes({value_name}.encode())"
                elif origin_type is bytearray:
                    return f"bytearray(decodebytes({value_name}.encode()))"
            elif issubclass(origin_type, str):
                return value_name
            elif issubclass(origin_type, typing.List):
                if is_generic(ftype):
                    return f"[{inner_expr()} for value in {value_name}]"
                elif ftype is list:
                    raise UnserializableField(
                        fname, ftype, parent, "Use typing.List[T] instead"
                    )
            elif issubclass(origin_type, typing.Deque):
                if is_generic(ftype):
                    return (
                        f"collections.deque([{inner_expr()} "
                        f"for value in {value_name}])"
                    )
                elif ftype is collections.deque:
                    raise UnserializableField(
                        fname, ftype, parent, "Use typing.Deque[T] instead"
                    )
            elif issubclass(origin_type, typing.Tuple):
                if is_named_tuple(ftype):
                    return self._unpack_named_tuple(
                        fname,
                        ftype,
                        value_name,
                        parent,
                        metadata,
                        deserialize_option,
                    )
                elif is_generic(ftype):
                    return self._unpack_tuple(
                        fname, value_name, args, parent, metadata
                    )
                elif ftype is tuple:
                    raise UnserializableField(
                        fname, ftype, parent, "Use typing.Tuple[T] instead"
                    )
            elif issubclass(origin_type, typing.FrozenSet):
                if is_generic(ftype):
                    return (
                        f"frozenset([{inner_expr()} "
                        f"for value in {value_name}])"
                    )
                elif ftype is frozenset:
                    raise UnserializableField(
                        fname, ftype, parent, "Use typing.FrozenSet[T] instead"
                    )
            elif issubclass(origin_type, typing.AbstractSet):
                if is_generic(ftype):
                    return f"set([{inner_expr()} for value in {value_name}])"
                elif ftype is set:
                    raise UnserializableField(
                        fname, ftype, parent, "Use typing.Set[T] instead"
                    )
            elif issubclass(origin_type, typing.ChainMap):
                if is_generic(ftype):
                    if args and is_dataclass(args[0]):
                        raise UnserializableDataError(
                            "ChainMaps with dataclasses as keys "
                            "are not supported by mashumaro"
                        )
                    else:
                        return (
                            f"collections.ChainMap("
                            f'*[{{{inner_expr(0,"key")}:{inner_expr(1)} '
                            f"for key, value in m.items()}} "
                            f"for m in {value_name}])"
                        )
                elif ftype is collections.ChainMap:
                    raise UnserializableField(
                        fname,
                        ftype,
                        parent,
                        "Use typing.ChainMap[KT,VT] instead",
                    )
            elif issubclass(origin_type, typing_extensions.OrderedDict):
                if is_generic(ftype):
                    if args and is_dataclass(args[0]):
                        raise UnserializableDataError(
                            "OrderedDict with dataclasses as keys "
                            "are not supported by mashumaro"
                        )
                    else:
                        return (
                            f"collections.OrderedDict("
                            f'{{{inner_expr(0,"key")}: {inner_expr(1)} '
                            f"for key, value in {value_name}.items()}})"
                        )
                elif ftype is collections.OrderedDict:
                    raise UnserializableField(
                        fname,
                        ftype,
                        parent,
                        "Use typing.OrderedDict[KT,VT] instead",
                    )
            elif issubclass(origin_type, typing.Counter):
                if is_generic(ftype):
                    if args and is_dataclass(args[0]):
                        raise UnserializableDataError(
                            "Counter with dataclasses as keys "
                            "are not supported by mashumaro"
                        )
                    else:
                        return (
                            f"collections.Counter("
                            f'{{{inner_expr(0,"key")}: '
                            f"{inner_expr(1, v_type=int)} "
                            f"for key, value in {value_name}.items()}})"
                        )
                elif ftype is collections.Counter:
                    raise UnserializableField(
                        fname,
                        ftype,
                        parent,
                        "Use typing.Counter[KT] instead",
                    )
            elif issubclass(origin_type, typing.Mapping):
                if is_typed_dict(ftype):
                    return self._unpack_typed_dict(
                        fname, ftype, value_name, parent, metadata
                    )
                elif is_generic(ftype):
                    if args and is_dataclass(args[0]):
                        raise UnserializableDataError(
                            "Mappings with dataclasses as keys "
                            "are not supported by mashumaro"
                        )
                    else:
                        return (
                            f'{{{inner_expr(0,"key")}: {inner_expr(1)} '
                            f"for key, value in {value_name}.items()}}"
                        )
                elif ftype is dict:
                    raise UnserializableField(
                        fname,
                        ftype,
                        parent,
                        "Use typing.Dict[KT,VT] or Mapping[KT,VT] instead",
                    )
            elif issubclass(origin_type, typing.Sequence):
                if is_generic(ftype):
                    return f"[{inner_expr()} for value in {value_name}]"
        elif issubclass(origin_type, os.PathLike):
            if issubclass(origin_type, pathlib.PosixPath):
                return f"pathlib.PosixPath({value_name})"
            elif issubclass(origin_type, pathlib.WindowsPath):
                return f"pathlib.WindowsPath({value_name})"
            elif issubclass(origin_type, pathlib.Path):
                return f"pathlib.Path({value_name})"
            elif issubclass(origin_type, pathlib.PurePosixPath):
                return f"pathlib.PurePosixPath({value_name})"
            elif issubclass(origin_type, pathlib.PureWindowsPath):
                return f"pathlib.PureWindowsPath({value_name})"
            elif issubclass(origin_type, pathlib.PurePath):
                return f"pathlib.PurePath({value_name})"
            elif origin_type is os.PathLike:
                return f"pathlib.PurePath({value_name})"
            else:
                return f"{type_name(origin_type)}({value_name})"
        elif issubclass(origin_type, enum.Enum):
            return f"{type_name(origin_type)}({value_name})"

        raise UnserializableField(fname, ftype, parent)

    def _pack_union(
        self, fname, ftype, value_name, args, parent, metadata, prefix="union"
    ) -> str:
        lines = CodeLines()
        method_name = (
            f"__pack_{prefix}_{parent.__name__}_{fname}__"
            f"{str(uuid.uuid4().hex)}"
        )
        default_kwargs = self.get_to_dict_default_flag_values()
        if default_kwargs:
            lines.append(f"def {method_name}(self, value, {default_kwargs}):")
        else:
            lines.append(f"def {method_name}(self, value):")
        with lines.indent():
            for packer in (
                self._pack_value(fname, arg_type, parent, metadata=metadata)
                for arg_type in args
            ):
                lines.append("try:")
                with lines.indent():
                    lines.append(f"return {packer}")
                lines.append("except:")
                with lines.indent():
                    lines.append("pass")
            field_type = type_name(
                ftype, type_vars=self._get_field_type_vars(fname)
            )
            lines.append(
                f"raise InvalidFieldValue('{fname}',{field_type},value,cls)"
            )
        lines.append(f"setattr(cls, '{method_name}', {method_name})")
        if self.get_config().debug:
            print(f"{type_name(self.cls)}:")
            print(lines.as_text())
        exec(lines.as_text(), self.globals, self.__dict__)
        method_args = ", ".join(
            filter(None, (value_name, self.get_to_dict_flags()))
        )
        return f"self.{method_name}({method_args})"

    def _unpack_union(
        self, fname, ftype, value_name, args, parent, metadata, prefix="union"
    ) -> str:
        lines = CodeLines()
        method_name = (
            f"__unpack_{prefix}_{parent.__name__}_{fname}__"
            f"{str(uuid.uuid4().hex)}"
        )
        default_kwargs = self.get_from_dict_default_flag_values()
        lines.append("@classmethod")
        if default_kwargs:
            lines.append(f"def {method_name}(cls, value, {default_kwargs}):")
        else:
            lines.append(f"def {method_name}(cls, value):")
        with lines.indent():
            for unpacker in (
                self._unpack_field_value(
                    fname, arg_type, parent, metadata=metadata
                )
                for arg_type in args
            ):
                lines.append("try:")
                with lines.indent():
                    lines.append(f"return {unpacker}")
                lines.append("except:")
                with lines.indent():
                    lines.append("pass")
            field_type = type_name(
                ftype, type_vars=self._get_field_type_vars(fname)
            )
            lines.append(
                f"raise InvalidFieldValue('{fname}',{field_type},value,cls)"
            )
        lines.append(f"setattr(cls, '{method_name}', {method_name})")
        if self.get_config().debug:
            print(f"{type_name(self.cls)}:")
            print(lines.as_text())
        exec(lines.as_text(), self.globals, self.__dict__)
        method_args = ", ".join(
            filter(None, (value_name, self.get_from_dict_flags()))
        )
        return f"cls.{method_name}({method_args})"

    def _pack_tuple(self, fname, value_name, args, parent, metadata) -> str:
        if not args:
            args = [typing.Any, ...]
        if len(args) == 1 and args[0] == ():
            return "[]"
        elif len(args) == 2 and args[1] is Ellipsis:
            packer = self._pack_value(
                fname,
                args[0],
                parent,
                value_name,
                metadata=metadata,
                could_be_none=True,
            )
            return f"[{packer} for value in value]"
        else:
            packers = [
                self._pack_value(
                    fname,
                    arg_type,
                    parent,
                    f"{value_name}[{arg_idx}]",
                    metadata=metadata,
                    could_be_none=True,
                )
                for arg_idx, arg_type in enumerate(args)
            ]
            return f"[{', '.join(packers)}]"

    def _unpack_tuple(self, fname, value_name, args, parent, metadata) -> str:
        if not args:
            args = [typing.Any, ...]
        if len(args) == 1 and args[0] == ():
            return "()"
        elif len(args) == 2 and args[1] is Ellipsis:
            unpacker = self._unpack_field_value(
                fname,
                args[0],
                parent,
                value_name,
                metadata=metadata,
                could_be_none=True,
            )
            return f"tuple([{unpacker} for value in value])"
        else:
            unpackers = [
                self._unpack_field_value(
                    fname,
                    arg_type,
                    parent,
                    f"{value_name}[{arg_idx}]",
                    metadata=metadata,
                    could_be_none=True,
                )
                for arg_idx, arg_type in enumerate(args)
            ]
            return f"tuple([{', '.join(unpackers)}])"

    def _pack_typed_dict(
        self, fname, ftype, value_name, parent, metadata
    ) -> str:
        annotations = ftype.__annotations__
        all_keys = list(annotations.keys())
        required_keys = getattr(ftype, "__required_keys__", all_keys)
        optional_keys = getattr(ftype, "__optional_keys__", [])
        lines = CodeLines()
        method_name = (
            f"__pack_typed_dict_{parent.__name__}_{fname}__"
            f"{str(uuid.uuid4().hex)}"
        )
        default_kwargs = self.get_to_dict_default_flag_values()
        if default_kwargs:
            lines.append(f"def {method_name}(self, value, {default_kwargs}):")
        else:
            lines.append(f"def {method_name}(self, value):")
        with lines.indent():
            lines.append("d = {}")
            for key in sorted(required_keys, key=all_keys.index):
                packer = self._pack_value(
                    fname,
                    annotations[key],
                    parent,
                    f"{value_name}['{key}']",
                    metadata=metadata,
                    could_be_none=True,
                )
                lines.append(f"d['{key}'] = {packer}")
            for key in sorted(optional_keys, key=all_keys.index):
                lines.append(f"key_value = {value_name}.get('{key}', MISSING)")
                lines.append("if key_value is not MISSING:")
                with lines.indent():
                    packer = self._pack_value(
                        fname,
                        annotations[key],
                        parent,
                        "key_value",
                        metadata=metadata,
                        could_be_none=True,
                    )
                    lines.append(f"d['{key}'] = {packer}")
            lines.append("return d")
        lines.append(f"setattr(cls, '{method_name}', {method_name})")
        if self.get_config().debug:
            print(f"{type_name(self.cls)}:")
            print(lines.as_text())
        exec(lines.as_text(), self.globals, self.__dict__)
        method_args = ", ".join(
            filter(None, (value_name, self.get_to_dict_flags()))
        )
        return f"self.{method_name}({method_args})"

    def _unpack_typed_dict(
        self, fname, ftype, value_name, parent, metadata
    ) -> str:
        annotations = ftype.__annotations__
        all_keys = list(annotations.keys())
        required_keys = getattr(ftype, "__required_keys__", all_keys)
        optional_keys = getattr(ftype, "__optional_keys__", [])
        lines = CodeLines()
        method_name = (
            f"__unpack_typed_dict_{parent.__name__}_{fname}__"
            f"{str(uuid.uuid4().hex)}"
        )
        default_kwargs = self.get_from_dict_default_flag_values()
        lines.append("@classmethod")
        if default_kwargs:
            lines.append(f"def {method_name}(cls, value, {default_kwargs}):")
        else:
            lines.append(f"def {method_name}(cls, value):")
        with lines.indent():
            lines.append("d = {}")
            for key in sorted(required_keys, key=all_keys.index):
                unpacker = self._unpack_field_value(
                    fname,
                    annotations[key],
                    parent,
                    f"{value_name}['{key}']",
                    metadata=metadata,
                    could_be_none=True,
                )
                lines.append(f"d['{key}'] = {unpacker}")
            for key in sorted(optional_keys, key=all_keys.index):
                lines.append(f"key_value = {value_name}.get('{key}', MISSING)")
                lines.append("if key_value is not MISSING:")
                with lines.indent():
                    unpacker = self._unpack_field_value(
                        fname,
                        annotations[key],
                        parent,
                        "key_value",
                        metadata=metadata,
                        could_be_none=True,
                    )
                    lines.append(f"d['{key}'] = {unpacker}")
            lines.append("return d")
        lines.append(f"setattr(cls, '{method_name}', {method_name})")
        if self.get_config().debug:
            print(f"{type_name(self.cls)}:")
            print(lines.as_text())
        exec(lines.as_text(), self.globals, self.__dict__)
        method_args = ", ".join(
            filter(None, (value_name, self.get_from_dict_flags()))
        )
        return f"cls.{method_name}({method_args})"

    def _pack_named_tuple(
        self, fname, ftype, value_name, parent, metadata, serialize_option
    ) -> str:
        annotations = getattr(ftype, "__annotations__", {})
        fields = getattr(ftype, "_fields", ())
        packers = []
        as_dict = self.get_config().namedtuple_as_dict
        if serialize_option is not None:
            if serialize_option == "as_dict":
                as_dict = True
            elif serialize_option == "as_list":
                as_dict = False
            else:
                raise UnsupportedSerializationEngine(
                    fname, ftype, parent, serialize_option
                )
        for idx, field in enumerate(fields):
            packer = self._pack_value(
                fname,
                annotations.get(field, typing.Any),
                parent,
                f"{value_name}[{idx}]",
                metadata=metadata,
                could_be_none=True,
            )
            packers.append(packer)
        if as_dict:
            kv = (f"'{key}': {value}" for key, value in zip(fields, packers))
            return f"{{{', '.join(kv)}}}"
        else:
            return f"[{', '.join(packers)}]"

    def _unpack_named_tuple(
        self, fname, ftype, value_name, parent, metadata, deserialize_option
    ) -> str:
        annotations = getattr(ftype, "__annotations__", {})
        fields = getattr(ftype, "_fields", ())
        defaults = getattr(ftype, "_field_defaults", {})
        unpackers = []
        as_dict = self.get_config().namedtuple_as_dict
        if deserialize_option is not None:
            if deserialize_option == "as_dict":
                as_dict = True
            elif deserialize_option == "as_list":
                as_dict = False
            else:
                raise UnsupportedDeserializationEngine(
                    fname, ftype, parent, deserialize_option
                )
        if as_dict:
            field_indices = zip((f"'{name}'" for name in fields), fields)
        else:
            field_indices = enumerate(fields)  # type: ignore
        for idx, field in field_indices:
            unpacker = self._unpack_field_value(
                fname,
                annotations.get(field, typing.Any),
                parent,
                f"{value_name}[{idx}]",
                metadata=metadata,
                could_be_none=True,
            )
            unpackers.append(unpacker)

        if not defaults:
            return f"{type_name(ftype)}({', '.join(unpackers)})"

        lines = CodeLines()
        method_name = (
            f"__unpack_named_tuple_{parent.__name__}_{fname}__"
            f"{str(uuid.uuid4().hex)}"
        )
        lines.append("@classmethod")
        default_kwargs = self.get_from_dict_default_flag_values()
        if default_kwargs:
            lines.append(f"def {method_name}(cls, value, {default_kwargs}):")
        else:
            lines.append(f"def {method_name}(cls, value):")
        with lines.indent():
            lines.append("fields = []")
            lines.append("try:")
            with lines.indent():
                for unpacker in unpackers:
                    lines.append(f"fields.append({unpacker})")
            lines.append("except IndexError:")
            with lines.indent():
                lines.append("pass")
            lines.append(f"return {type_name(ftype)}(*fields)")
        lines.append(f"setattr(cls, '{method_name}', {method_name})")
        if self.get_config().debug:
            print(f"{type_name(self.cls)}:")
            print(lines.as_text())
        exec(lines.as_text(), self.globals, self.__dict__)
        method_args = ", ".join(
            filter(None, (value_name, self.get_from_dict_flags()))
        )
        return f"cls.{method_name}({method_args})"

    def _unpack_literal(
        self, fname, ftype, value_name, parent, metadata
    ) -> str:
        lines = CodeLines()
        method_name = (
            f"__unpack_literal_{parent.__name__}_{fname}__"
            f"{str(uuid.uuid4().hex)}"
        )
        default_kwargs = self.get_from_dict_default_flag_values()
        lines.append("@classmethod")
        if default_kwargs:
            lines.append(f"def {method_name}(cls, value, {default_kwargs}):")
        else:
            lines.append(f"def {method_name}(cls, value):")
        with lines.indent():
            for literal_value in get_literal_values(ftype):
                if isinstance(literal_value, enum.Enum):
                    enum_type_name = type_name(type(literal_value))
                    lines.append(
                        f"if {value_name} == {enum_type_name}."
                        f"{literal_value.name}.value:"
                    )
                    with lines.indent():
                        lines.append(
                            f"return {enum_type_name}.{literal_value.name}"
                        )
                elif isinstance(literal_value, bytes):
                    unpacker = self._unpack_field_value(
                        fname, bytes, parent, value_name, metadata
                    )
                    lines.append("try:")
                    with lines.indent():
                        lines.append(f"if {unpacker} == {literal_value!r}:")
                        with lines.indent():
                            lines.append(f"return {literal_value!r}")
                    lines.append("except:")
                    with lines.indent():
                        lines.append("pass")
                elif isinstance(  # type: ignore
                    literal_value, (int, str, bool, NoneType)  # type: ignore
                ):
                    lines.append(f"if {value_name} == {literal_value!r}:")
                    with lines.indent():
                        lines.append(f"return {literal_value!r}")
            lines.append(f"raise ValueError({value_name})")
        lines.append(f"setattr(cls, '{method_name}', {method_name})")
        if self.get_config().debug:
            print(f"{type_name(self.cls)}:")
            print(lines.as_text())
        exec(lines.as_text(), self.globals, self.__dict__)
        method_args = ", ".join(
            filter(None, (value_name, self.get_from_dict_flags()))
        )
        return f"cls.{method_name}({method_args})"

    def _pack_literal(self, fname, ftype, value_name, parent, metadata) -> str:
        self._add_type_modules(ftype)
        lines = CodeLines()
        method_name = (
            f"__pack_literal_{parent.__name__}_{fname}__"
            f"{str(uuid.uuid4().hex)}"
        )
        default_kwargs = self.get_to_dict_default_flag_values()
        if default_kwargs:
            lines.append(f"def {method_name}(self, value, {default_kwargs}):")
        else:
            lines.append(f"def {method_name}(self, value):")
        with lines.indent():
            for literal_value in get_literal_values(ftype):
                value_type = type(literal_value)
                if isinstance(literal_value, enum.Enum):
                    enum_type_name = type_name(
                        value_type, type_vars=self._get_field_type_vars(fname)
                    )
                    lines.append(
                        f"if {value_name} == {enum_type_name}."
                        f"{literal_value.name}:"
                    )
                    with lines.indent():
                        packer = self._pack_value(
                            fname, value_type, parent, value_name, metadata
                        )
                        lines.append(f"return {packer}")
                elif isinstance(  # type: ignore
                    literal_value,
                    (int, str, bytes, bool, NoneType),  # type: ignore
                ):
                    lines.append(f"if {value_name} == {literal_value!r}:")
                    with lines.indent():
                        packer = self._pack_value(
                            fname, value_type, parent, value_name, metadata
                        )
                        lines.append(f"return {packer}")
            field_type = type_name(
                ftype, type_vars=self._get_field_type_vars(fname)
            )
            lines.append(
                f"raise InvalidFieldValue('{fname}',"
                f"{field_type},{value_name},type(self))"
            )
        lines.append(f"setattr(cls, '{method_name}', {method_name})")
        if self.get_config().debug:
            print(f"{type_name(self.cls)}:")
            print(lines.as_text())
        exec(lines.as_text(), self.globals, self.__dict__)
        method_args = ", ".join(
            filter(None, (value_name, self.get_to_dict_flags()))
        )
        return f"self.{method_name}({method_args})"

    @classmethod
    def _hash_arg_types(cls, arg_types) -> str:
        return md5(",".join(map(type_name, arg_types)).encode()).hexdigest()
