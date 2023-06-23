import importlib
import inspect
import types
import typing
from contextlib import contextmanager

# noinspection PyProtectedMember
from dataclasses import _FIELDS  # type: ignore
from dataclasses import MISSING, Field, is_dataclass
from functools import lru_cache

try:
    from dataclasses import KW_ONLY  # type: ignore
except ImportError:
    KW_ONLY = object()  # type: ignore

import typing_extensions

from mashumaro.config import (
    ADD_DIALECT_SUPPORT,
    ADD_SERIALIZATION_CONTEXT,
    TO_DICT_ADD_BY_ALIAS_FLAG,
    TO_DICT_ADD_OMIT_NONE_FLAG,
    BaseConfig,
    SerializationStrategyValueType,
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
    hash_type_args,
    is_class_var,
    is_dataclass_dict_mixin,
    is_dialect_subclass,
    is_init_var,
    is_literal,
    is_optional,
    is_type_var_any,
    resolve_type_params,
    substitute_type_params,
    type_name,
)
from mashumaro.core.meta.types.common import FieldContext, ValueSpec
from mashumaro.core.meta.types.pack import PackerRegistry
from mashumaro.core.meta.types.unpack import (
    SubtypeUnpackerBuilder,
    UnpackerRegistry,
)
from mashumaro.dialect import Dialect
from mashumaro.exceptions import (  # noqa
    BadDialect,
    BadHookSignature,
    InvalidFieldValue,
    MissingDiscriminatorError,
    MissingField,
    SuitableVariantNotFoundError,
    ThirdPartyModuleNotFoundError,
    UnresolvedTypeReferenceError,
    UnserializableDataError,
    UnserializableField,
    UnsupportedDeserializationEngine,
    UnsupportedSerializationEngine,
)
from mashumaro.types import Discriminator

__PRE_SERIALIZE__ = "__pre_serialize__"
__PRE_DESERIALIZE__ = "__pre_deserialize__"
__POST_SERIALIZE__ = "__post_serialize__"
__POST_DESERIALIZE__ = "__post_deserialize__"


class CodeBuilder:
    def __init__(
        self,
        cls: typing.Type,
        type_args: typing.Tuple[typing.Type, ...] = (),
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
        self.resolved_type_params: typing.Dict[
            typing.Type, typing.Dict[typing.Type, typing.Type]
        ] = {}
        self.field_classes: typing.Dict = {}
        self.initial_type_args = type_args
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
        self.resolved_type_params = resolve_type_params(
            self.cls, self.initial_type_args
        )
        self.field_classes = {}

    @property
    def namespace(self) -> typing.Mapping[typing.Any, typing.Any]:
        return self.cls.__dict__

    @property
    def annotations(self) -> typing.Dict[str, typing.Any]:
        return self.namespace.get("__annotations__", {})

    def __get_field_types(
        self, recursive: bool = True, include_extras: bool = False
    ) -> typing.Dict[str, typing.Any]:
        fields = {}
        try:
            field_type_hints = typing_extensions.get_type_hints(
                self.cls, include_extras=include_extras
            )
        except NameError as e:
            name = get_name_error_name(e)
            raise UnresolvedTypeReferenceError(self.cls, name) from None
        for fname, ftype in field_type_hints.items():
            if is_class_var(ftype) or is_init_var(ftype) or ftype is KW_ONLY:
                continue
            if recursive or fname in self.annotations:
                fields[fname] = ftype
        return fields

    def _get_field_class(self, field_name: str) -> typing.Any:
        try:
            cls = self.field_classes[field_name]
        except KeyError:
            cls = get_class_that_defines_field(field_name, self.cls)
            self.field_classes[field_name] = cls
        return cls

    def _get_real_type(
        self, field_name: str, field_type: typing.Type
    ) -> typing.Type:
        cls = self._get_field_class(field_name)
        return substitute_type_params(
            field_type, self.resolved_type_params[cls]
        )

    def get_field_resolved_type_params(
        self, field_name: str
    ) -> typing.Dict[typing.Type, typing.Type]:
        cls = self._get_field_class(field_name)
        return self.resolved_type_params[cls]

    def get_field_types(
        self, include_extras: bool = False
    ) -> typing.Dict[str, typing.Any]:
        return self.__get_field_types(include_extras=include_extras)

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

    def add_type_modules(self, *types_: typing.Type) -> None:
        for t in types_:
            module = inspect.getmodule(t)
            if not module:
                continue
            self.ensure_module_imported(module)
            if is_literal(t):
                literal_args = get_literal_values(t)
                self.add_type_modules(*literal_args)
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
    def indent(
        self,
        expr: typing.Optional[str] = None,
    ) -> typing.Generator[None, None, None]:
        with self.lines.indent(expr):
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
        cls = get_class_that_defines_method(method_name, self.cls)
        if cls is not None and not is_dataclass_dict_mixin(cls):
            return cls.__dict__[method_name]

    def _add_unpack_method_lines_lazy(self, method_name: str) -> None:
        if self.default_dialect is not None:
            self.add_type_modules(self.default_dialect)
        self.add_line(
            f"CodeBuilder("
            f"cls,"
            f"first_method='{method_name}',"
            f"allow_postponed_evaluation=False,"
            f"format_name='{self.format_name}',"
            f"decoder={type_name(self.decoder)},"  # type: ignore
            f"default_dialect={type_name(self.default_dialect)}"
            f").add_unpack_method()"
        )
        unpacker_args = [
            "d",
            self.get_unpack_method_flags(pass_decoder=True),
        ]
        unpacker_args_s = ", ".join(filter(None, unpacker_args))
        self.add_line(f"return cls.{method_name}({unpacker_args_s})")

    def _add_unpack_method_lines(self, method_name: str) -> None:
        config = self.get_config()
        if config.lazy_compilation and self.allow_postponed_evaluation:
            self._add_unpack_method_lines_lazy(method_name)
            return
        try:
            field_types = self.get_field_types(include_extras=True)
        except UnresolvedTypeReferenceError:
            if (
                not self.allow_postponed_evaluation
                or not config.allow_postponed_evaluation
            ):
                raise
            self._add_unpack_method_lines_lazy(method_name)
        else:
            if self.decoder is not None:
                self.add_line("d = decoder(d)")
            discr = self.get_discriminator()
            if discr:
                if not discr.include_subtypes:
                    raise ValueError(
                        "Config based discriminator must have "
                        "'include_subtypes' enabled"
                    )
                discr = Discriminator(
                    # prevent RecursionError
                    field=discr.field,
                    include_subtypes=discr.include_subtypes,
                )
                self.add_type_modules(self.cls)
                method = SubtypeUnpackerBuilder(discr).build(
                    spec=ValueSpec(
                        type=self.cls,
                        expression="d",
                        builder=self,
                        field_ctx=FieldContext("", {}),
                    )
                )
                self.add_line(f"return {method}")
                return
            pre_deserialize = self.get_declared_hook(__PRE_DESERIALIZE__)
            if pre_deserialize:
                if not isinstance(pre_deserialize, classmethod):
                    raise BadHookSignature(
                        f"`{__PRE_DESERIALIZE__}` must be a class method with "
                        f"Callable[[Dict[Any, Any]], Dict[Any, Any]] signature"
                    )
                else:
                    self.add_line(f"d = cls.{__PRE_DESERIALIZE__}(d)")
            post_deserialize = self.get_declared_hook(__POST_DESERIALIZE__)
            if post_deserialize:
                if not isinstance(post_deserialize, classmethod):
                    raise BadHookSignature(
                        f"`{__POST_DESERIALIZE__}` must be a class method "
                        f"with Callable[[{type_name(self.cls)}], "
                        f"{type_name(self.cls)}] signature"
                    )
            filtered_fields = []
            pos_args = []
            kw_args = []
            missing_kw_only = False
            can_be_kwargs = False
            for fname, ftype in field_types.items():
                field = self.dataclass_fields.get(fname)  # type: ignore
                # https://github.com/python/mypy/issues/1362
                if field and not field.init:
                    continue
                if self.get_field_default(fname) is MISSING:
                    if missing_kw_only:
                        kw_args.append(fname)
                    elif field:
                        kw_only = getattr(field, "kw_only", MISSING)
                        if kw_only is MISSING:
                            kw_args.append(fname)
                            missing_kw_only = True
                        elif kw_only:
                            kw_args.append(fname)
                        else:
                            pos_args.append(fname)
                    else:
                        kw_args.append(fname)
                        missing_kw_only = True
                else:
                    can_be_kwargs = True
                filtered_fields.append((fname, ftype))
            if filtered_fields:
                with self.indent("try:"):
                    if can_be_kwargs:
                        self.add_line("kwargs = {}")
                    for fname, ftype in filtered_fields:
                        self.add_type_modules(ftype)
                        metadata = self.metadatas.get(fname, {})
                        alias = metadata.get("alias")
                        if alias is None:
                            alias = config.aliases.get(fname)
                        self._unpack_method_set_value(
                            fname, ftype, metadata, alias=alias
                        )
                with self.indent("except TypeError:"):
                    with self.indent("if not isinstance(d, dict):"):
                        self.add_line(
                            f"raise ValueError('Argument for "
                            f"{type_name(self.cls)}.{method_name} method "
                            f"should be a dict instance') from None"
                        )
                    with self.indent("else:"):
                        self.add_line("raise")

            args = [f"__{f}" for f in pos_args]
            for kw_arg in kw_args:
                args.append(f"{kw_arg}=__{kw_arg}")
            if can_be_kwargs:
                args.append("**kwargs")
            cls_inst = f"cls({', '.join(args)})"

            if post_deserialize:
                self.add_line(f"return cls.{__POST_DESERIALIZE__}({cls_inst})")
            else:
                self.add_line(f"return {cls_inst}")

    def _add_unpack_method_with_dialect_lines(self, method_name: str) -> None:
        if self.decoder is not None:
            self.add_line("d = decoder(d)")
        unpacker_args = ", ".join(
            filter(None, ("cls", "d", self.get_unpack_method_flags()))
        )
        cache_name = f"__dialect_{self.format_name}_unpacker_cache__"
        self.add_line(f"unpacker = cls.{cache_name}.get(dialect)")
        with self.indent("if unpacker is not None:"):
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
            type_args=self.initial_type_args,
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
            with self.indent(f"if not '{cache_name}' in cls.__dict__:"):
                self.add_line(f"cls.{cache_name} = {{}}")

        if self.dialect is None:
            self.add_line("@classmethod")
        self._add_unpack_method_definition(method_name)
        with self.indent():
            if dialects_feature and self.dialect is None:
                with self.indent("if dialect is None:"):
                    self._add_unpack_method_lines(method_name)
                with self.indent("else:"):
                    self._add_unpack_method_with_dialect_lines(method_name)
            else:
                self._add_unpack_method_lines(method_name)
        if self.dialect is None:
            self.add_line(f"setattr(cls, '{method_name}', {method_name})")
        else:
            self.add_line(f"cls.{cache_name}[dialect] = {method_name}")
        self.compile()

    def _add_unpack_method_definition(self, method_name: str) -> None:
        kwargs = ""
        default_kwargs = self.get_unpack_method_default_flag_values(
            pass_decoder=True
        )
        if default_kwargs:
            kwargs += f", {default_kwargs}"
        self.add_line(f"def {method_name}(cls, d{kwargs}):")

    def _unpack_method_set_value(
        self,
        fname: str,
        ftype: typing.Type,
        metadata: typing.Mapping,
        *,
        alias: typing.Optional[str] = None,
    ) -> None:
        default = self.get_field_default(fname)
        has_default = default is not MISSING
        field_type = type_name(
            ftype,
            resolved_type_params=self.get_field_resolved_type_params(fname),
        )
        could_be_none = (
            ftype in (typing.Any, type(None), None)
            or is_type_var_any(self._get_real_type(fname, ftype))
            or is_optional(ftype, self.get_field_resolved_type_params(fname))
            or default is None
        )
        unpacked_value = UnpackerRegistry.get(
            ValueSpec(
                type=ftype,
                expression="value",
                builder=self,
                field_ctx=FieldContext(
                    name=fname,
                    metadata=metadata,
                ),
                could_be_none=False if could_be_none else True,
            )
        )
        if unpacked_value != "value":
            self.add_line(f"value = d.get('{alias or fname}', MISSING)")
            packed_value = "value"
        elif has_default:
            self.add_line(f"value = d.get('{alias or fname}', MISSING)")
            packed_value = "value"
        else:
            self.add_line(f"__{fname} = d.get('{alias or fname}', MISSING)")
            packed_value = f"__{fname}"
            unpacked_value = packed_value
        if not has_default:
            with self.indent(f"if {packed_value} is MISSING:"):
                self.add_line(
                    f"raise MissingField('{fname}',{field_type},cls) "
                    f"from None"
                )
            if packed_value != unpacked_value:
                if could_be_none:
                    with self.indent(f"if {packed_value} is not None:"):
                        self.__unpack_try_set_value(
                            fname, field_type, unpacked_value, has_default
                        )
                    with self.indent("else:"):
                        self.__unpack_set_value(fname, "None", has_default)
                else:
                    self.__unpack_try_set_value(
                        fname, field_type, unpacked_value, has_default
                    )
        else:
            with self.indent(f"if {packed_value} is not MISSING:"):
                if could_be_none:
                    with self.indent(f"if {packed_value} is not None:"):
                        self.__unpack_try_set_value(
                            fname, field_type, unpacked_value, has_default
                        )
                    if default is not None:
                        with self.indent("else:"):
                            self.__unpack_set_value(fname, "None", has_default)
                else:
                    self.__unpack_try_set_value(
                        fname, field_type, unpacked_value, has_default
                    )

    def __unpack_try_set_value(
        self,
        field_name: str,
        field_type_name: str,
        unpacked_value: str,
        has_default: bool,
    ) -> None:
        with self.indent("try:"):
            self.__unpack_set_value(field_name, unpacked_value, has_default)
        with self.indent("except:"):
            self.add_line(
                f"raise InvalidFieldValue("
                f"'{field_name}',{field_type_name},value,cls)"
            )

    def __unpack_set_value(
        self, fname: str, unpacked_value: str, in_kwargs: bool
    ) -> None:
        if in_kwargs:
            self.add_line(f"kwargs['{fname}'] = {unpacked_value}")
        else:
            self.add_line(f"__{fname} = {unpacked_value}")

    @lru_cache()
    @typing.no_type_check
    def get_config(
        self,
        cls: typing.Optional[typing.Type] = None,
        look_in_parents: bool = True,
    ) -> typing.Type[BaseConfig]:
        if cls is None:
            cls = self.cls
        if look_in_parents:
            config_cls = getattr(cls, "Config", BaseConfig)
        else:
            config_cls = self.namespace.get("Config", BaseConfig)
        if not issubclass(config_cls, BaseConfig):
            config_cls = type(
                "Config",
                (BaseConfig, config_cls),
                {**BaseConfig.__dict__, **config_cls.__dict__},
            )
        return config_cls

    def get_discriminator(self) -> typing.Optional[Discriminator]:
        return self.get_config(look_in_parents=False).discriminator

    def get_pack_method_flags(
        self,
        cls: typing.Optional[typing.Type] = None,
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
            (ADD_SERIALIZATION_CONTEXT, "context"),
        ):
            if self.is_code_generation_option_enabled(option, cls):
                if self.is_code_generation_option_enabled(option):
                    pluggable_flags.append(f"{flag}={flag}")
        return ", ".join(pluggable_flags)

    def get_unpack_method_flags(
        self,
        cls: typing.Optional[typing.Type] = None,
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
        cls: typing.Optional[typing.Type] = None,
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

        context_feature = self.is_code_generation_option_enabled(
            ADD_SERIALIZATION_CONTEXT, cls
        )
        if context_feature:
            kw_param_names.append("context")
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
        self, pass_decoder: bool = False
    ) -> str:
        pos_param_names = []
        pos_param_values = []
        kw_param_names = []
        kw_param_values = []

        if pass_decoder and self.decoder is not None:
            pos_param_names.append("decoder")
            pos_param_values.append(type_name(self.decoder))

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

    def is_code_generation_option_enabled(
        self, option: str, cls: typing.Optional[typing.Type] = None
    ) -> bool:
        if cls is None:
            cls = self.cls
        return option in self.get_config(cls).code_generation_options

    @classmethod
    def get_unpack_method_name(
        cls,
        type_args: typing.Iterable = (),
        format_name: str = "dict",
        decoder: typing.Optional[typing.Any] = None,
    ) -> str:
        if format_name != "dict" and decoder is not None:
            return f"from_{format_name}"
        else:
            method_name = "from_dict"
            if format_name != "dict":
                method_name += f"_{format_name}"
            if type_args:
                method_name += f"_{hash_type_args(type_args)}"
            return method_name

    @classmethod
    def get_pack_method_name(
        cls,
        type_args: typing.Tuple[typing.Type, ...] = (),
        format_name: str = "dict",
        encoder: typing.Optional[typing.Any] = None,
    ) -> str:
        if format_name != "dict" and encoder is not None:
            return f"to_{format_name}"
        else:
            method_name = "to_dict"
            if format_name != "dict":
                method_name += f"_{format_name}"
            if type_args:
                method_name += f"_{hash_type_args(type_args)}"
            return method_name

    def _add_pack_method_lines_lazy(self, method_name: str) -> None:
        if self.default_dialect is not None:
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

    def _add_pack_method_lines(self, method_name: str) -> None:
        config = self.get_config()
        if config.lazy_compilation and self.allow_postponed_evaluation:
            self._add_pack_method_lines_lazy(method_name)
            return
        try:
            field_types = self.get_field_types(include_extras=True)
        except UnresolvedTypeReferenceError:
            if (
                not self.allow_postponed_evaluation
                or not config.allow_postponed_evaluation
            ):
                raise
            self._add_pack_method_lines_lazy(method_name)
        else:
            pre_serialize = self.get_declared_hook(__PRE_SERIALIZE__)
            if pre_serialize:
                if self.is_code_generation_option_enabled(
                    ADD_SERIALIZATION_CONTEXT
                ):
                    pre_serialize_args = "context=context"
                else:
                    pre_serialize_args = ""
                self.add_line(
                    f"self = self.{__PRE_SERIALIZE__}({pre_serialize_args})"
                )
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
                if self.metadatas.get(fname, {}).get("serialize") == "omit":
                    continue
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
                        with self.indent("if value is not None:"):
                            self._pack_method_set_value(
                                fname, alias, by_alias_feature, packer
                            )
                        if omit_none and not omit_none_feature:
                            continue
                        with self.indent("else:"):
                            if omit_none_feature:
                                with self.indent("if not omit_none:"):
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
                if self.is_code_generation_option_enabled(
                    ADD_SERIALIZATION_CONTEXT
                ):
                    kwargs = f"{kwargs}, context=context"
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
            with self.indent("if by_alias:"):
                self.add_line(f"kwargs['{alias}'] = {packed_value}")
            with self.indent("else:"):
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

    def _get_encoder_kwargs(
        self, cls: typing.Optional[typing.Type] = None
    ) -> typing.Dict[str, typing.Any]:
        result = {}
        for encoder_param, value in self.encoder_kwargs.items():
            packer_param = value[0]
            packer_value = value[1]
            if isinstance(packer_value, ConfigValue):
                packer_value = getattr(self.get_config(cls), packer_value.name)
            result[encoder_param] = (packer_param, packer_value)
        return result

    def _add_pack_method_definition(self, method_name: str) -> None:
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
            type_args=self.initial_type_args,
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
            with self.indent(f"if not '{cache_name}' in cls.__dict__:"):
                self.add_line(f"cls.{cache_name} = {{}}")

        self._add_pack_method_definition(method_name)
        with self.indent():
            if dialects_feature and self.dialect is None:
                with self.indent("if dialect is None:"):
                    self._add_pack_method_lines(method_name)
                with self.indent("else:"):
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
        fname: str,
        ftype: typing.Type,
        config: typing.Type[BaseConfig],
    ) -> typing.Tuple[str, typing.Optional[str], bool]:
        metadata = self.metadatas.get(fname, {})
        alias = metadata.get("alias")
        if alias is None:
            alias = config.aliases.get(fname)
        could_be_none = (
            ftype in (typing.Any, type(None), None)
            or is_type_var_any(self._get_real_type(fname, ftype))
            or is_optional(ftype, self.get_field_resolved_type_params(fname))
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

    @typing.no_type_check
    def iter_serialization_strategies(
        self, metadata: typing.Mapping, ftype: typing.Type
    ) -> typing.Iterator[SerializationStrategyValueType]:
        yield metadata.get("serialization_strategy")
        yield from self.__iter_serialization_strategies(ftype)

    @typing.no_type_check
    def __iter_serialization_strategies(
        self, ftype: typing.Type
    ) -> typing.Iterator[SerializationStrategyValueType]:
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
        cls: typing.Optional[typing.Type] = None,
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
