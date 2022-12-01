import importlib
import inspect
import sys
import types
import typing
from contextlib import contextmanager

# noinspection PyProtectedMember
from dataclasses import _FIELDS, MISSING, Field, is_dataclass  # type: ignore
from functools import lru_cache
from hashlib import md5

from mashumaro.config import (
    ADD_DIALECT_SUPPORT,
    TO_DICT_ADD_BY_ALIAS_FLAG,
    TO_DICT_ADD_OMIT_NONE_FLAG,
    BaseConfig,
)
from mashumaro.core.const import Sentinel
from mashumaro.core.helpers import ConfigValue
from mashumaro.core.meta.code.lines import CodeLines
from mashumaro.core.meta.helpers import (
    get_args,
    get_class_that_defines_field,
    get_class_that_defines_method,
    get_literal_values,
    get_name_error_name,
    is_class_var,
    is_dataclass_dict_mixin,
    is_dialect_subclass,
    is_init_var,
    is_literal,
    is_named_tuple,
    is_optional,
    is_type_var_any,
    resolve_type_vars,
    type_name,
)
from mashumaro.core.meta.types.common import FieldContext, ValueSpec
from mashumaro.core.meta.types.pack import PackerRegistry
from mashumaro.core.meta.types.unpack import UnpackerRegistry
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

__PRE_SERIALIZE__ = "__pre_serialize__"
__PRE_DESERIALIZE__ = "__pre_deserialize__"
__POST_SERIALIZE__ = "__post_serialize__"
__POST_DESERIALIZE__ = "__post_deserialize__"


class CodeBuilder:
    def __init__(
        self,
        cls,
        arg_types: typing.Tuple = (),
        dialect: typing.Optional[typing.Type[Dialect]] = None,
        first_method: str = "from_dict",
        allow_postponed_evaluation: bool = True,
        format_name: str = "dict",
        decoder: typing.Optional[typing.Any] = None,
        encoder: typing.Optional[typing.Any] = None,
        encoder_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None,
        default_dialect: typing.Optional[typing.Type[Dialect]] = None,
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
        self.default_dialect = default_dialect
        self.allow_postponed_evaluation = allow_postponed_evaluation
        self.format_name = format_name
        self.decoder = decoder
        self.encoder = encoder
        self.encoder_kwargs = encoder_kwargs or {}

    def reset(self) -> None:
        self.lines.reset()
        self.globals = globals().copy()
        self.type_vars = resolve_type_vars(self.cls, self.initial_arg_types)
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

    def _get_real_type(self, field_name, field_type) -> typing.Any:
        cls = self._get_field_class(field_name)
        return self.type_vars[cls].get(field_type, field_type)

    def get_field_type_vars(self, field_name) -> typing.Dict[str, typing.Any]:
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

    def add_type_modules(self, *types_) -> None:
        for t in types_:
            module = inspect.getmodule(t)
            if not module:
                continue
            self.ensure_module_imported(module)
            if is_literal(t):
                args = get_literal_values(t)
                self.add_type_modules(*args)
            else:
                args = get_args(t)
                if args:
                    self.add_type_modules(*args)
            constraints = getattr(t, "__constraints__", ())
            if constraints:
                self.add_type_modules(*constraints)
            bound = getattr(t, "__bound__", ())
            if bound:
                self.add_type_modules(bound)

    def ensure_module_imported(self, module: types.ModuleType) -> None:
        self.globals.setdefault(module.__name__, module)
        package = module.__name__.split(".")[0]
        self.globals.setdefault(package, importlib.import_module(package))

    def ensure_object_imported(
        self,
        obj: typing.Any,
        name: typing.Optional[str] = None,
    ) -> None:
        self.globals.setdefault(name or obj.__name__, obj)

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

    def _add_unpack_method_lines(self, method_name: str) -> None:
        config = self.get_config()
        try:
            field_types = self.field_types
        except UnresolvedTypeReferenceError:
            if (
                not self.allow_postponed_evaluation
                or not config.allow_postponed_evaluation
            ):
                raise
            self.add_type_modules(self.default_dialect)
            self.add_line(
                f"CodeBuilder("
                f"cls,"
                f"first_method='{method_name}',"
                f"allow_postponed_evaluation=False,"
                f"format_name='{self.format_name}',"
                f"decoder={type_name(self.decoder)},"
                f"default_dialect={type_name(self.default_dialect)}"
                f").add_unpack_method()"
            )
            unpacker_args = [
                "d",
                self.get_unpack_method_flags(pass_decoder=True),
            ]
            unpacker_args_s = ", ".join(filter(None, unpacker_args))
            self.add_line(f"return cls.{method_name}({unpacker_args_s})")
        else:
            if self.decoder is not None:
                self.add_line("d = decoder(d)")
            pre_deserialize = self.get_declared_hook(__PRE_DESERIALIZE__)
            if pre_deserialize:
                if not isinstance(pre_deserialize, classmethod):
                    raise BadHookSignature(
                        f"`{__PRE_DESERIALIZE__}` must be a class method with "
                        f"Callable[[Dict[Any, Any]], Dict[Any, Any]] signature"
                    )
                else:
                    self.add_line(f"d = cls.{__PRE_DESERIALIZE__}(d)")
            filtered_fields = []
            for fname, ftype in field_types.items():
                field = self.dataclass_fields.get(fname)  # type: ignore
                # https://github.com/python/mypy/issues/1362
                if field and not field.init:
                    continue
                filtered_fields.append((fname, ftype))
            if filtered_fields:
                self.add_line("try:")
                with self.indent():
                    self.add_line("kwargs = {}")
                    for fname, ftype in filtered_fields:
                        self.add_type_modules(ftype)
                        metadata = self.metadatas.get(fname, {})
                        alias = metadata.get("alias")
                        if alias is None:
                            alias = config.aliases.get(fname)
                        self._unpack_method_set_value(
                            fname, ftype, metadata, alias
                        )
                self.add_line("except TypeError:")
                with self.indent():
                    self.add_line("if not isinstance(d, dict):")
                    with self.indent():
                        self.add_line(
                            f"raise ValueError('Argument for "
                            f"{type_name(self.cls)}.{method_name} method "
                            f"should be a dict instance') from None"
                        )
                    self.add_line("else:")
                    with self.indent():
                        self.add_line("raise")
            else:
                self.add_line("kwargs = {}")
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

    def _add_unpack_method_with_dialect_lines(self, method_name: str) -> None:
        if self.decoder is not None:
            self.add_line("d = decoder(d)")
        unpacker_args = ", ".join(
            filter(None, ("cls", "d", self.get_unpack_method_flags()))
        )
        cache_name = f"__dialect_{self.format_name}_unpacker_cache__"
        self.add_line(f"unpacker = cls.{cache_name}.get(dialect)")
        self.add_line("if unpacker is not None:")
        with self.indent():
            self.add_line(f"return unpacker({unpacker_args})")
        if self.default_dialect:
            self.add_type_modules(self.default_dialect)
        self.add_line(
            f"CodeBuilder("
            f"cls,dialect=dialect,"
            f"first_method='{method_name}',"
            f"format_name='{self.format_name}',"
            f"default_dialect={type_name(self.default_dialect)}"
            f").add_unpack_method()"
        )
        self.add_line(f"return cls.{cache_name}[dialect]({unpacker_args})")

    def add_unpack_method(self) -> None:
        self.reset()
        method_name = self.get_unpack_method_name(
            arg_types=self.initial_arg_types,
            format_name=self.format_name,
            decoder=self.decoder,
        )
        if self.decoder is not None:
            self.add_type_modules(self.decoder)
        dialects_feature = self.is_code_generation_option_enabled(
            ADD_DIALECT_SUPPORT
        )
        cache_name = f"__dialect_{self.format_name}_unpacker_cache__"
        if dialects_feature:
            self.add_line(f"if not '{cache_name}' in cls.__dict__:")
            with self.indent():
                self.add_line(f"cls.{cache_name} = {{}}")

        if self.dialect is None:
            self.add_line("@classmethod")
        self._add_unpack_method_definition(method_name)
        with self.indent():
            if dialects_feature and self.dialect is None:
                self.add_line("if dialect is None:")
                with self.indent():
                    self._add_unpack_method_lines(method_name)
                self.add_line("else:")
                with self.indent():
                    self._add_unpack_method_with_dialect_lines(method_name)
            else:
                self._add_unpack_method_lines(method_name)
        if self.dialect is None:
            self.add_line(f"setattr(cls, '{method_name}', {method_name})")
        else:
            self.add_line(f"cls.{cache_name}[dialect] = {method_name}")
        self.compile()

    def _add_unpack_method_definition(self, method_name: str):
        kwargs = ""
        default_kwargs = self.get_unpack_method_default_flag_values(
            pass_decoder=True
        )
        if default_kwargs:
            kwargs += f", {default_kwargs}"
        self.add_line(f"def {method_name}(cls, d{kwargs}):")

    def _unpack_method_set_value(
        self, fname, ftype, metadata, alias=None
    ) -> None:
        self.add_line("try:")
        with self.indent():
            if is_named_tuple(ftype):
                self.add_line(f"value = d['{alias or fname}']")
                packed_value = "value"
            else:
                packed_value = f"d['{alias or fname}']"
            unpacked_value = UnpackerRegistry.get(
                ValueSpec(
                    type=ftype,
                    expression=packed_value,
                    builder=self,
                    field_ctx=FieldContext(
                        name=fname,
                        metadata=metadata,
                    ),
                )
            )
            self.add_line(f"kwargs['{fname}'] = {unpacked_value}")
        self.add_line("except KeyError as e:")
        with self.indent():
            field_type = type_name(
                ftype, type_vars=self.get_field_type_vars(fname)
            )
            if self.get_field_default(fname) is MISSING:
                self.add_line("if e.__traceback__.tb_next is None:")
                with self.indent():
                    self.add_line(
                        f"raise MissingField('{fname}',{field_type},cls) "
                        f"from None"
                    )
                self.add_line("else:")
                with self.indent():
                    self.add_line(
                        f"raise InvalidFieldValue("
                        f"'{fname}',{field_type},{packed_value},cls)"
                    )
            else:
                self.add_line("if e.__traceback__.tb_next is not None:")
                with self.indent():
                    self.add_line(
                        f"raise InvalidFieldValue("
                        f"'{fname}',{field_type},{packed_value},cls)"
                    )
        self.add_line("except Exception:")
        with self.indent():
            self.add_line(
                f"raise InvalidFieldValue("
                f"'{fname}',{field_type},{packed_value},cls)"
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

    def get_pack_method_flags(
        self,
        cls=None,
        pass_encoder: bool = False,
    ) -> str:
        pluggable_flags = []
        if pass_encoder and self.encoder is not None:
            pluggable_flags.append("encoder=encoder")
            for value in self._get_encoder_kwargs(cls).values():
                pluggable_flags.append(f"{value[0]}={value[0]}")

        for option, flag in (
            (TO_DICT_ADD_OMIT_NONE_FLAG, "omit_none"),
            (TO_DICT_ADD_BY_ALIAS_FLAG, "by_alias"),
            (ADD_DIALECT_SUPPORT, "dialect"),
        ):
            if self.is_code_generation_option_enabled(option, cls):
                if self.is_code_generation_option_enabled(option):
                    pluggable_flags.append(f"{flag}={flag}")
        return ", ".join(pluggable_flags)

    def get_unpack_method_flags(
        self,
        cls=None,
        pass_decoder: bool = False,
    ) -> str:
        pluggable_flags = []
        if pass_decoder and self.decoder is not None:
            pluggable_flags.append("decoder=decoder")
        for option, flag in ((ADD_DIALECT_SUPPORT, "dialect"),):
            if self.is_code_generation_option_enabled(option, cls):
                if self.is_code_generation_option_enabled(option):
                    pluggable_flags.append(f"{flag}={flag}")
        return ", ".join(pluggable_flags)

    def get_pack_method_default_flag_values(
        self,
        cls=None,
        pass_encoder: bool = False,
    ) -> str:
        pos_param_names = []
        pos_param_values = []
        kw_param_names = []
        kw_param_values = []
        if pass_encoder and self.encoder is not None:
            pos_param_names.append("encoder")
            pos_param_values.append(type_name(self.encoder))
            for value in self._get_encoder_kwargs(cls).values():
                kw_param_names.append(value[0])
                kw_param_values.append(value[1])
        omit_none_feature = self.is_code_generation_option_enabled(
            TO_DICT_ADD_OMIT_NONE_FLAG, cls
        )
        if omit_none_feature:
            omit_none = self._get_dialect_or_config_option(
                "omit_none", False, None
            )
            kw_param_names.append("omit_none")
            kw_param_values.append("True" if omit_none else "False")
        by_alias_feature = self.is_code_generation_option_enabled(
            TO_DICT_ADD_BY_ALIAS_FLAG, cls
        )
        if by_alias_feature:
            serialize_by_alias = self.get_config(cls).serialize_by_alias
            kw_param_names.append("by_alias")
            kw_param_values.append("True" if serialize_by_alias else "False")
        dialects_feature = self.is_code_generation_option_enabled(
            ADD_DIALECT_SUPPORT, cls
        )
        if dialects_feature:
            kw_param_names.append("dialect")
            kw_param_values.append("None")
        if pos_param_names:
            pluggable_flags_str = ", ".join(
                [f"{n}={v}" for n, v in zip(pos_param_names, pos_param_values)]
            )
        else:
            pluggable_flags_str = ""
        if kw_param_names:
            if pos_param_names:
                pluggable_flags_str += ", "
            pluggable_flags_str += "*, " + ", ".join(
                [f"{n}={v}" for n, v in zip(kw_param_names, kw_param_values)]
            )
        return pluggable_flags_str

    def get_unpack_method_default_flag_values(
        self,
        cls=None,
        pass_decoder: bool = False,
    ) -> str:
        pos_param_names = []
        pos_param_values = []
        kw_param_names = []
        kw_param_values = []
        if pass_decoder and self.decoder is not None:
            pos_param_names.append("decoder")
            pos_param_values.append(type_name(self.decoder))
        dialects_feature = self.is_code_generation_option_enabled(
            ADD_DIALECT_SUPPORT, cls
        )
        if dialects_feature:
            kw_param_names.append("dialect")
            kw_param_values.append("None")
        if pos_param_names:
            pluggable_flags_str = ", ".join(
                [f"{n}={v}" for n, v in zip(pos_param_names, pos_param_values)]
            )
        else:
            pluggable_flags_str = ""
        if kw_param_names:
            if pos_param_names:
                pluggable_flags_str += ", "
            pluggable_flags_str += "*, " + ", ".join(
                [f"{n}={v}" for n, v in zip(kw_param_names, kw_param_values)]
            )
        return pluggable_flags_str

    def is_code_generation_option_enabled(self, option: str, cls=None) -> bool:
        if cls is None:
            cls = self.cls
        return option in self.get_config(cls).code_generation_options

    @classmethod
    def get_unpack_method_name(
        cls,
        arg_types: typing.Tuple = (),
        format_name: str = "dict",
        decoder: typing.Optional[typing.Any] = None,
    ) -> str:
        if format_name != "dict" and decoder is not None:
            return f"from_{format_name}"
        else:
            method_name = "from_dict"
            if format_name != "dict":
                method_name += f"_{format_name}"
            if arg_types:
                method_name += f"_{cls._hash_arg_types(arg_types)}"
            return method_name

    @classmethod
    def get_pack_method_name(
        cls,
        arg_types: typing.Tuple = (),
        format_name: str = "dict",
        encoder: typing.Optional[typing.Any] = None,
    ) -> str:
        if format_name != "dict" and encoder is not None:
            return f"to_{format_name}"
        else:
            method_name = "to_dict"
            if format_name != "dict":
                method_name += f"_{format_name}"
            if arg_types:
                method_name += f"_{cls._hash_arg_types(arg_types)}"
            return method_name

    def _add_pack_method_lines(self, method_name: str) -> None:
        config = self.get_config()
        try:
            field_types = self.field_types
        except UnresolvedTypeReferenceError:
            if (
                not self.allow_postponed_evaluation
                or not config.allow_postponed_evaluation
            ):
                raise
            self.add_type_modules(self.default_dialect)
            self.add_line(
                f"CodeBuilder("
                f"self.__class__,"
                f"first_method='{method_name}',"
                f"allow_postponed_evaluation=False,"
                f"format_name='{self.format_name}',"
                f"encoder={type_name(self.encoder)},"
                f"encoder_kwargs={self._get_encoder_kwargs()},"
                f"default_dialect={type_name(self.default_dialect)}"
                f").add_pack_method()"
            )
            packer_args = self.get_pack_method_flags(pass_encoder=True)
            self.add_line(f"return self.{method_name}({packer_args})")
        else:
            pre_serialize = self.get_declared_hook(__PRE_SERIALIZE__)
            if pre_serialize:
                self.add_line(f"self = self.{__PRE_SERIALIZE__}()")
            by_alias_feature = self.is_code_generation_option_enabled(
                TO_DICT_ADD_BY_ALIAS_FLAG
            )
            omit_none_feature = self.is_code_generation_option_enabled(
                TO_DICT_ADD_OMIT_NONE_FLAG
            )
            serialize_by_alias = self.get_config().serialize_by_alias
            omit_none = self._get_dialect_or_config_option("omit_none", False)
            packers = {}
            aliases = {}
            fields_could_be_none = set()
            for fname, ftype in field_types.items():
                packer, alias, could_be_none = self._get_field_packer(
                    fname, ftype, config
                )
                packers[fname] = packer
                if alias:
                    aliases[fname] = alias
                if could_be_none:
                    fields_could_be_none.add(fname)
            if fields_could_be_none or by_alias_feature and aliases:
                kwargs = "kwargs"
                self.add_line("kwargs = {}")
                for fname, packer in packers.items():
                    alias = aliases.get(fname)
                    if fname in fields_could_be_none:
                        self.add_line(f"value = self.{fname}")
                        self.add_line("if value is not None:")
                        with self.indent():
                            self._pack_method_set_value(
                                fname, alias, by_alias_feature, packer
                            )
                        if omit_none and not omit_none_feature:
                            continue
                        self.add_line("else:")
                        with self.indent():
                            if omit_none_feature:
                                self.add_line("if not omit_none:")
                                with self.indent():
                                    self._pack_method_set_value(
                                        fname, alias, by_alias_feature, "None"
                                    )
                            else:
                                self._pack_method_set_value(
                                    fname, alias, by_alias_feature, "None"
                                )
                    else:
                        self._pack_method_set_value(
                            fname, alias, by_alias_feature, packer
                        )
            else:
                kwargs_parts = []
                for fname, packer in packers.items():
                    if serialize_by_alias:
                        fname_or_alias = aliases.get(fname, fname)
                    else:
                        fname_or_alias = fname
                    kwargs_parts.append((fname_or_alias, packer))
                kwargs = ", ".join(f"'{k}': {v}" for k, v in kwargs_parts)
                kwargs = f"{{{kwargs}}}"
            post_serialize = self.get_declared_hook(__POST_SERIALIZE__)
            if self.encoder is not None:
                if self.encoder_kwargs:
                    encoder_options = ", ".join(
                        f"{k}={v[0]}" for k, v in self.encoder_kwargs.items()
                    )
                    return_statement = (
                        f"return encoder({{}}, {encoder_options})"
                    )
                else:
                    return_statement = "return encoder({})"
            else:
                return_statement = "return {}"
            if post_serialize:
                self.add_line(
                    return_statement.format(
                        f"self.{__POST_SERIALIZE__}({kwargs})"
                    )
                )
            else:
                self.add_line(return_statement.format(kwargs))

    def _pack_method_set_value(
        self,
        fname: str,
        alias: typing.Optional[str],
        by_alias_feature: bool,
        packed_value: str,
    ) -> None:
        if by_alias_feature and alias is not None:
            self.add_line("if by_alias:")
            with self.indent():
                self.add_line(f"kwargs['{alias}'] = {packed_value}")
            self.add_line("else:")
            with self.indent():
                self.add_line(f"kwargs['{fname}'] = {packed_value}")
        else:
            serialize_by_alias = self.get_config().serialize_by_alias
            if serialize_by_alias and alias is not None:
                fname_or_alias = alias
            else:
                fname_or_alias = fname
            self.add_line(f"kwargs['{fname_or_alias}'] = {packed_value}")

    def _add_pack_method_with_dialect_lines(self, method_name: str) -> None:
        packer_args = ", ".join(
            filter(None, ("self", self.get_pack_method_flags()))
        )
        cache_name = f"__dialect_{self.format_name}_packer_cache__"
        self.add_line(f"packer = self.__class__.{cache_name}.get(dialect)")
        self.add_line("if packer is not None:")
        if self.encoder is not None:
            return_statement = "return encoder({})"
        else:
            return_statement = "return {}"
        with self.indent():
            self.add_line(return_statement.format(f"packer({packer_args})"))
        if self.default_dialect:
            self.add_type_modules(self.default_dialect)
        self.add_line(
            f"CodeBuilder("
            f"self.__class__,dialect=dialect,"
            f"first_method='{method_name}',"
            f"format_name='{self.format_name}',"
            f"default_dialect={type_name(self.default_dialect)}"
            f").add_pack_method()"
        )
        self.add_line(
            return_statement.format(
                f"self.__class__.{cache_name}[dialect]({packer_args})"
            )
        )

    def _get_encoder_kwargs(self, cls=None) -> typing.Dict[str, typing.Any]:
        result = {}
        for encoder_param, value in self.encoder_kwargs.items():
            packer_param = value[0]
            packer_value = value[1]
            if isinstance(packer_value, ConfigValue):
                packer_value = getattr(self.get_config(cls), packer_value.name)
            result[encoder_param] = (packer_param, packer_value)
        return result

    def _add_pack_method_definition(self, method_name: str):
        kwargs = ""
        default_kwargs = self.get_pack_method_default_flag_values(
            pass_encoder=True
        )
        if default_kwargs:
            kwargs += f", {default_kwargs}"
        self.add_line(f"def {method_name}(self{kwargs}):")

    def add_pack_method(self) -> None:
        self.reset()
        method_name = self.get_pack_method_name(
            arg_types=self.initial_arg_types,
            format_name=self.format_name,
            encoder=self.encoder,
        )
        if self.encoder is not None:
            self.add_type_modules(self.encoder)
        dialects_feature = self.is_code_generation_option_enabled(
            ADD_DIALECT_SUPPORT
        )
        cache_name = f"__dialect_{self.format_name}_packer_cache__"
        if dialects_feature:
            self.add_line(f"if not '{cache_name}' in cls.__dict__:")
            with self.indent():
                self.add_line(f"cls.{cache_name} = {{}}")

        self._add_pack_method_definition(method_name)
        with self.indent():
            if dialects_feature and self.dialect is None:
                self.add_line("if dialect is None:")
                with self.indent():
                    self._add_pack_method_lines(method_name)
                self.add_line("else:")
                with self.indent():
                    self._add_pack_method_with_dialect_lines(method_name)
            else:
                self._add_pack_method_lines(method_name)
        if self.dialect is None:
            self.add_line(f"setattr(cls, '{method_name}', {method_name})")
        else:
            self.add_line(f"cls.{cache_name}[dialect] = {method_name}")
        self.compile()

    def _get_field_packer(
        self,
        fname,
        ftype,
        config,
    ) -> typing.Tuple[str, typing.Optional[str], bool]:
        metadata = self.metadatas.get(fname, {})
        alias = metadata.get("alias")
        if alias is None:
            alias = config.aliases.get(fname)
        could_be_none = (
            ftype in (typing.Any, type(None), None)
            or is_type_var_any(ftype)
            or is_optional(ftype, self.get_field_type_vars(fname))
            or self.get_field_default(fname) is None
        )
        value = "value" if could_be_none else f"self.{fname}"
        packer = PackerRegistry.get(
            ValueSpec(
                type=ftype,
                expression=value,
                builder=self,
                field_ctx=FieldContext(
                    name=fname,
                    metadata=metadata,
                ),
                could_be_none=False,
            )
        )
        return packer, alias, could_be_none

    def iter_serialization_strategies(self, metadata, ftype):
        yield metadata.get("serialization_strategy")
        yield from self.__iter_serialization_strategies(ftype)

    @lru_cache()
    def __iter_serialization_strategies(self, ftype):
        if self.dialect is not None:
            yield self.dialect.serialization_strategy.get(ftype)
        default_dialect = self.get_config().dialect
        if default_dialect is not None:
            if not is_dialect_subclass(default_dialect):
                raise BadDialect(
                    f'Config option "dialect" of '
                    f"{type_name(self.cls)} must be a subclass of Dialect"
                )
            yield default_dialect.serialization_strategy.get(ftype)
        yield self.get_config().serialization_strategy.get(ftype)
        if self.default_dialect is not None:
            yield self.default_dialect.serialization_strategy.get(ftype)

    def _get_dialect_or_config_option(
        self,
        option: str,
        default: typing.Any,
        cls=None,
    ) -> typing.Any:
        for ns in (
            self.dialect,
            self.get_config(cls).dialect,
            self.get_config(cls),
            self.default_dialect,
        ):
            value = getattr(ns, option, Sentinel.MISSING)
            if value is not Sentinel.MISSING:
                return value
        return default

    @classmethod
    def _hash_arg_types(cls, arg_types) -> str:
        return md5(",".join(map(type_name, arg_types)).encode()).hexdigest()
