import collections
import collections.abc
import datetime
import enum
import ipaddress
import os
import pathlib
import types
import typing
import uuid
from base64 import decodebytes
from contextlib import suppress
from decimal import Decimal
from fractions import Fraction
from typing import Any, Callable, Iterable, List, Optional, Tuple, Type, Union

import typing_extensions

from mashumaro.core.const import PY_39_MIN, PY_311_MIN
from mashumaro.core.helpers import parse_timezone
from mashumaro.core.meta.code.lines import CodeLines
from mashumaro.core.meta.helpers import (
    collect_type_params,
    get_args,
    get_class_that_defines_method,
    get_function_arg_annotation,
    get_literal_values,
    is_dataclass_dict_mixin_subclass,
    is_generic,
    is_literal,
    is_named_tuple,
    is_new_type,
    is_not_required,
    is_optional,
    is_required,
    is_self,
    is_special_typing_primitive,
    is_type_var,
    is_type_var_any,
    is_type_var_tuple,
    is_typed_dict,
    is_union,
    is_unpack,
    not_none_type_arg,
    resolve_type_params,
    type_name,
)
from mashumaro.core.meta.types.common import (
    Expression,
    ExpressionWrapper,
    NoneType,
    Registry,
    ValueSpec,
    ensure_generic_collection,
    ensure_generic_collection_subclass,
    ensure_generic_mapping,
    expr_or_maybe_none,
)
from mashumaro.exceptions import (
    ThirdPartyModuleNotFoundError,
    UnserializableDataError,
    UnserializableField,
    UnsupportedDeserializationEngine,
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
    ciso8601: Optional[types.ModuleType] = None  # type: ignore
try:
    import pendulum
except ImportError:  # pragma no cover
    pendulum: Optional[types.ModuleType] = None  # type: ignore


__all__ = ["UnpackerRegistry"]


UnpackerRegistry = Registry()
register = UnpackerRegistry.register


def _unpack_with_annotated_serialization_strategy(
    spec: ValueSpec,
    strategy: SerializationStrategy,
) -> Expression:
    strategy_type = type(strategy)
    try:
        value_type: Union[Type, Any] = get_function_arg_annotation(
            strategy.deserialize,
            arg_pos=0,
        )
    except (KeyError, ValueError):
        value_type = Any
    resolved = resolve_type_params(strategy_type, get_args(spec.type))[
        strategy_type
    ]
    new_type_args = []
    for type_param in collect_type_params(value_type):
        new_type_args.append(resolved.get(type_param, type_param))
    with suppress(TypeError):
        value_type = value_type[tuple(new_type_args)]
    overridden_fn = f"__{spec.field_ctx.name}_deserialize_{uuid.uuid4().hex}"
    setattr(spec.builder.cls, overridden_fn, strategy.deserialize)
    unpacker = UnpackerRegistry.get(spec.copy(type=value_type))
    return f"cls.{overridden_fn}({unpacker})"


def get_overridden_deserialization_method(
    spec: ValueSpec,
) -> Optional[Union[Callable, str, ExpressionWrapper]]:
    deserialize_option = spec.field_ctx.metadata.get("deserialize")
    if deserialize_option is not None:
        return deserialize_option
    for typ in (spec.type, spec.origin_type):
        for strategy in spec.builder.iter_serialization_strategies(
            spec.field_ctx.metadata, typ
        ):
            if strategy is pass_through:
                return pass_through
            elif isinstance(strategy, dict):
                deserialize_option = strategy.get("deserialize")
            elif isinstance(strategy, SerializationStrategy):
                if strategy.__use_annotations__ or is_generic(type(strategy)):
                    return ExpressionWrapper(
                        _unpack_with_annotated_serialization_strategy(
                            spec=spec,
                            strategy=strategy,
                        )
                    )
                deserialize_option = strategy.deserialize
            if deserialize_option is not None:
                return deserialize_option


@register
def unpack_type_with_overridden_deserialization(
    spec: ValueSpec,
) -> Optional[Expression]:
    deserialization_method = get_overridden_deserialization_method(spec)
    if deserialization_method is pass_through:
        return spec.expression
    elif isinstance(deserialization_method, ExpressionWrapper):
        return deserialization_method.expression
    elif callable(deserialization_method):
        overridden_fn = (
            f"__{spec.field_ctx.name}_deserialize_{uuid.uuid4().hex}"
        )
        setattr(spec.builder.cls, overridden_fn, deserialization_method)
        return f"cls.{overridden_fn}({spec.expression})"


def _unpack_annotated_serializable_type(
    spec: ValueSpec,
) -> Optional[Expression]:
    try:
        # noinspection PyProtectedMember
        # noinspection PyUnresolvedReferences
        value_type = get_function_arg_annotation(
            spec.origin_type._deserialize,
            arg_pos=0,
        )
    except (KeyError, ValueError):
        raise UnserializableField(
            field_name=spec.field_ctx.name,
            field_type=spec.type,
            holder_class=spec.builder.cls,
            msg='Method _deserialize must have annotated "value" argument',
        ) from None
    if is_self(value_type):
        return f"{type_name(spec.type)}._deserialize({spec.expression})"
    type_args = get_args(value_type)
    resolved = resolve_type_params(spec.origin_type, get_args(spec.type))[
        spec.origin_type
    ]
    new_type_args = []
    for type_arg in type_args:
        new_type_args.append(resolved.get(type_arg, type_arg))
    with suppress(TypeError):
        # noinspection PyUnresolvedReferences
        value_type = value_type[tuple(new_type_args)]
    unpacker = UnpackerRegistry.get(spec.copy(type=value_type))
    return f"{type_name(spec.type)}._deserialize({unpacker})"


@register
def unpack_serializable_type(spec: ValueSpec) -> Optional[Expression]:
    try:
        if not issubclass(spec.origin_type, SerializableType):
            return None
    except TypeError:
        return None
    if spec.origin_type.__use_annotations__:
        return _unpack_annotated_serializable_type(spec)
    else:
        return f"{type_name(spec.type)}._deserialize({spec.expression})"


@register
def unpack_generic_serializable_type(spec: ValueSpec) -> Optional[Expression]:
    with suppress(TypeError):
        if issubclass(spec.origin_type, GenericSerializableType):
            type_arg_names = ", ".join(
                list(map(type_name, get_args(spec.type)))
            )
            return (
                f"{type_name(spec.type)}._deserialize({spec.expression}, "
                f"[{type_arg_names}])"
            )


@register
def unpack_dataclass_dict_mixin_subclass(
    spec: ValueSpec,
) -> Optional[Expression]:
    if is_dataclass_dict_mixin_subclass(spec.origin_type):
        type_args = get_args(spec.type)
        method_name = spec.builder.get_unpack_method_name(
            type_args, spec.builder.format_name
        )
        if get_class_that_defines_method(
            method_name, spec.origin_type
        ) != spec.origin_type and (
            spec.origin_type != spec.builder.cls
            or spec.builder.get_unpack_method_name(
                type_args=type_args,
                format_name=spec.builder.format_name,
                decoder=spec.builder.decoder,
            )
            != method_name
        ):
            builder = spec.builder.__class__(
                spec.origin_type,
                type_args,
                dialect=spec.builder.dialect,
                format_name=spec.builder.format_name,
                default_dialect=spec.builder.default_dialect,
            )
            builder.add_unpack_method()
        method_args = ", ".join(
            filter(
                None,
                (
                    spec.expression,
                    spec.builder.get_unpack_method_flags(spec.type),
                ),
            )
        )
        return f"{type_name(spec.origin_type)}.{method_name}({method_args})"


@register
def unpack_any(spec: ValueSpec) -> Optional[Expression]:
    if spec.type is Any:
        return spec.expression


def unpack_union(
    spec: ValueSpec, args: Tuple[Type, ...], prefix: str = "union"
) -> Expression:
    lines = CodeLines()
    method_name = (
        f"__unpack_{prefix}_{spec.builder.cls.__name__}_"
        f"{spec.field_ctx.name}__{str(uuid.uuid4().hex)}"
    )
    default_kwargs = spec.builder.get_unpack_method_default_flag_values()
    lines.append("@classmethod")
    if default_kwargs:
        lines.append(f"def {method_name}(cls, value, {default_kwargs}):")
    else:
        lines.append(f"def {method_name}(cls, value):")
    with lines.indent():
        for unpacker in (
            UnpackerRegistry.get(spec.copy(type=type_arg, expression="value"))
            for type_arg in args
        ):
            lines.append("try:")
            with lines.indent():
                lines.append(f"return {unpacker}")
            lines.append("except:")
            with lines.indent():
                lines.append("pass")
        field_type = type_name(
            spec.type,
            resolved_type_params=spec.builder.get_field_resolved_type_params(
                spec.field_ctx.name
            ),
        )
        lines.append(
            f"raise InvalidFieldValue('{spec.field_ctx.name}',{field_type},"
            f"value,cls)"
        )
    lines.append(f"setattr(cls, '{method_name}', {method_name})")
    if spec.builder.get_config().debug:
        print(f"{type_name(spec.builder.cls)}:")
        print(lines.as_text())
    exec(lines.as_text(), spec.builder.globals, spec.builder.__dict__)
    method_args = ", ".join(
        filter(None, (spec.expression, spec.builder.get_unpack_method_flags()))
    )
    return f"cls.{method_name}({method_args})"


def unpack_literal(spec: ValueSpec) -> Expression:
    spec.builder.add_type_modules(spec.type)
    lines = CodeLines()
    method_name = (
        f"__unpack_literal_{spec.builder.cls.__name__}_{spec.field_ctx.name}__"
        f"{str(uuid.uuid4().hex)}"
    )
    default_kwargs = spec.builder.get_unpack_method_default_flag_values()
    lines.append("@classmethod")
    if default_kwargs:
        lines.append(f"def {method_name}(cls, value, {default_kwargs}):")
    else:
        lines.append(f"def {method_name}(cls, value):")
    with lines.indent():
        for literal_value in get_literal_values(spec.type):
            if isinstance(literal_value, enum.Enum):
                enum_type_name = type_name(type(literal_value))
                lines.append(
                    f"if value == {enum_type_name}.{literal_value.name}.value:"
                )
                with lines.indent():
                    lines.append(
                        f"return {enum_type_name}.{literal_value.name}"
                    )
            elif isinstance(literal_value, bytes):
                unpacker = UnpackerRegistry.get(
                    spec.copy(type=bytes, expression="value")
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
                literal_value,
                (int, str, bool, NoneType),  # type: ignore
            ):
                lines.append(f"if value == {literal_value!r}:")
                with lines.indent():
                    lines.append(f"return {literal_value!r}")
        lines.append("raise ValueError(value)")
    lines.append(f"setattr(cls, '{method_name}', {method_name})")
    if spec.builder.get_config().debug:
        print(f"{type_name(spec.builder.cls)}:")
        print(lines.as_text())
    exec(lines.as_text(), spec.builder.globals, spec.builder.__dict__)
    method_args = ", ".join(
        filter(None, (spec.expression, spec.builder.get_unpack_method_flags()))
    )
    return f"cls.{method_name}({method_args})"


@register
def unpack_special_typing_primitive(spec: ValueSpec) -> Optional[Expression]:
    if is_special_typing_primitive(spec.origin_type):
        if is_union(spec.type):
            resolved_type_params = spec.builder.get_field_resolved_type_params(
                spec.field_ctx.name
            )
            if is_optional(spec.type, resolved_type_params):
                arg = not_none_type_arg(
                    get_args(spec.type), resolved_type_params
                )
                uv = UnpackerRegistry.get(spec.copy(type=arg))
                return expr_or_maybe_none(spec, uv)
            else:
                return unpack_union(spec, get_args(spec.type))
        elif spec.origin_type is typing.AnyStr:
            raise UnserializableDataError(
                "AnyStr is not supported by mashumaro"
            )
        elif is_type_var_any(spec.type):
            return spec.expression
        elif is_type_var(spec.type):
            constraints = getattr(spec.type, "__constraints__")
            if constraints:
                return unpack_union(spec, constraints, "type_var")
            else:
                bound = getattr(spec.type, "__bound__")
                # act as if it was Optional[bound]
                uv = UnpackerRegistry.get(spec.copy(type=bound))
                return expr_or_maybe_none(spec, uv)
        elif is_new_type(spec.type):
            return UnpackerRegistry.get(
                spec.copy(type=spec.type.__supertype__)
            )
        elif is_literal(spec.type):
            return unpack_literal(spec)
        elif is_self(spec.type):
            method_name = spec.builder.get_unpack_method_name(
                format_name=spec.builder.format_name
            )
            if (
                get_class_that_defines_method(method_name, spec.builder.cls)
                != spec.builder.cls
                # not hasattr(spec.builder.cls, method_name)
                and spec.builder.get_unpack_method_name(
                    format_name=spec.builder.format_name,
                    decoder=spec.builder.decoder,
                )
                != method_name
            ):
                builder = spec.builder.__class__(
                    spec.builder.cls,
                    dialect=spec.builder.dialect,
                    format_name=spec.builder.format_name,
                    default_dialect=spec.builder.default_dialect,
                )
                builder.add_unpack_method()
            method_args = ", ".join(
                filter(
                    None,
                    (
                        spec.expression,
                        spec.builder.get_unpack_method_flags(spec.builder.cls),
                    ),
                )
            )
            spec.builder.add_type_modules(spec.builder.cls)
            return (
                f"{type_name(spec.builder.cls)}.{method_name}({method_args})"
            )
        elif is_required(spec.type) or is_not_required(spec.type):
            return UnpackerRegistry.get(spec.copy(type=get_args(spec.type)[0]))
        elif is_unpack(spec.type):
            unpacker = UnpackerRegistry.get(
                spec.copy(type=get_args(spec.type)[0])
            )
            return f"*{unpacker}"
        elif is_type_var_tuple(spec.type):
            return UnpackerRegistry.get(spec.copy(type=Tuple[Any, ...]))
        else:
            raise UnserializableDataError(
                f"{spec.type} as a field type is not supported by mashumaro"
            )


@register
def unpack_number(spec: ValueSpec) -> Optional[Expression]:
    if spec.origin_type in (int, float):
        return f"{type_name(spec.origin_type)}({spec.expression})"


@register
def unpack_bool_and_none(spec: ValueSpec) -> Optional[Expression]:
    if spec.origin_type in (bool, NoneType, None):
        return spec.expression


@register
def unpack_date_objects(spec: ValueSpec) -> Optional[Expression]:
    if spec.origin_type in (datetime.datetime, datetime.date, datetime.time):
        deserialize_option = get_overridden_deserialization_method(spec)
        if deserialize_option is not None:
            if deserialize_option == "ciso8601":
                if ciso8601:
                    spec.builder.ensure_module_imported(ciso8601)
                    datetime_parser = "ciso8601.parse_datetime"
                else:
                    raise ThirdPartyModuleNotFoundError(
                        "ciso8601", spec.field_ctx.name, spec.builder.cls
                    )  # pragma no cover
            elif deserialize_option == "pendulum":
                if pendulum:
                    spec.builder.ensure_module_imported(pendulum)
                    datetime_parser = "pendulum.parse"
                else:
                    raise ThirdPartyModuleNotFoundError(
                        "pendulum", spec.field_ctx.name, spec.builder.cls
                    )  # pragma no cover
            else:
                raise UnsupportedDeserializationEngine(
                    spec.field_ctx.name,
                    spec.type,
                    spec.builder.cls,
                    deserialize_option,
                )
            suffix = ""
            if spec.origin_type is datetime.date:
                suffix = ".date()"
            elif spec.origin_type is datetime.time:
                suffix = ".time()"
            return f"{datetime_parser}({spec.expression}){suffix}"
        method = f"__datetime_{spec.origin_type.__name__}_fromisoformat"
        spec.builder.ensure_object_imported(
            getattr(datetime, spec.origin_type.__name__).fromisoformat,
            method,
        )
        return f"{method}({spec.expression})"


@register
def unpack_timedelta(spec: ValueSpec) -> Optional[Expression]:
    if spec.origin_type is datetime.timedelta:
        method = "__datetime_timedelta"
        spec.builder.ensure_object_imported(datetime.timedelta, method)
        return f"{method}(seconds={spec.expression})"


@register
def unpack_timezone(spec: ValueSpec) -> Optional[Expression]:
    if spec.origin_type is datetime.timezone:
        spec.builder.ensure_object_imported(parse_timezone)
        return f"parse_timezone({spec.expression})"


@register
def unpack_zone_info(spec: ValueSpec) -> Optional[Expression]:
    if PY_39_MIN and spec.origin_type is zoneinfo.ZoneInfo:
        method = "__zoneinfo_ZoneInfo"
        spec.builder.ensure_object_imported(zoneinfo.ZoneInfo, method)
        return f"{method}({spec.expression})"


@register
def unpack_uuid(spec: ValueSpec) -> Optional[Expression]:
    if spec.origin_type is uuid.UUID:
        method = "__uuid_UUID"
        spec.builder.ensure_object_imported(uuid.UUID, method)
        return f"{method}({spec.expression})"


@register
def unpack_ipaddress(spec: ValueSpec) -> Optional[Expression]:
    if spec.origin_type in (
        ipaddress.IPv4Address,
        ipaddress.IPv6Address,
        ipaddress.IPv4Network,
        ipaddress.IPv6Network,
        ipaddress.IPv4Interface,
        ipaddress.IPv6Interface,
    ):
        method = f"__ipaddress_{spec.origin_type.__name__}"
        spec.builder.ensure_object_imported(spec.origin_type, method)
        return f"{method}({spec.expression})"


@register
def unpack_decimal(spec: ValueSpec) -> Optional[Expression]:
    if spec.origin_type is Decimal:
        spec.builder.ensure_object_imported(Decimal)
        return f"Decimal({spec.expression})"


@register
def unpack_fraction(spec: ValueSpec) -> Optional[Expression]:
    if spec.origin_type is Fraction:
        spec.builder.ensure_object_imported(Fraction)
        return f"Fraction({spec.expression})"


def unpack_tuple(spec: ValueSpec, args: Tuple[Type, ...]) -> Expression:
    if not args:
        if spec.type in (Tuple, tuple):
            args = [typing.Any, ...]  # type: ignore
        else:
            return "()"
    elif len(args) == 1 and args[0] == ():
        if not PY_311_MIN:
            return "()"
    if len(args) == 2 and args[1] is Ellipsis:
        unpacker = UnpackerRegistry.get(
            spec.copy(type=args[0], expression="value", could_be_none=True)
        )
        return f"tuple([{unpacker} for value in {spec.expression}])"
    else:
        arg_indexes: List[Union[int, Tuple[int, Union[int, None]]]] = []
        unpack_idx: Optional[int] = None
        for arg_idx, type_arg in enumerate(args):
            if is_unpack(type_arg):
                if unpack_idx is not None:
                    raise TypeError(
                        "Multiple unpacks are disallowed within a single type "
                        f"parameter list for {type_name(spec.type)}"
                    )
                unpack_idx = arg_idx
                if len(args) == 1:
                    arg_indexes.append((arg_idx, None))
                elif arg_idx < len(args) - 1:
                    arg_indexes.append((arg_idx, arg_idx + 1 - len(args)))
                else:
                    arg_indexes.append((arg_idx, None))
            else:
                if unpack_idx is None:
                    arg_indexes.append(arg_idx)
                else:
                    arg_indexes.append(arg_idx - len(args))
        unpackers: List[Expression] = []
        for _idx, _arg_idx in enumerate(arg_indexes):
            if isinstance(_arg_idx, tuple):
                u_expr = f"{spec.expression}[{_arg_idx[0]}:{_arg_idx[1]}]"
            else:
                u_expr = f"{spec.expression}[{_arg_idx}]"
            unpacker = UnpackerRegistry.get(
                spec.copy(
                    type=args[_idx],
                    expression=u_expr,
                    could_be_none=True,
                )
            )
            if unpacker != "*()":  # workaround for empty tuples
                unpackers.append(unpacker)
        return f"tuple([{', '.join(unpackers)}])"


def unpack_named_tuple(spec: ValueSpec) -> Expression:
    resolved = resolve_type_params(spec.origin_type, get_args(spec.type))[
        spec.origin_type
    ]
    annotations = {
        k: resolved.get(v, v)
        for k, v in getattr(spec.origin_type, "__annotations__", {}).items()
    }
    fields = getattr(spec.type, "_fields", ())
    defaults = getattr(spec.type, "_field_defaults", {})
    unpackers = []
    as_dict = spec.builder.get_config().namedtuple_as_dict
    deserialize_option = get_overridden_deserialization_method(spec)
    if deserialize_option is not None:
        if deserialize_option == "as_dict":
            as_dict = True
        elif deserialize_option == "as_list":
            as_dict = False
        else:
            raise UnsupportedDeserializationEngine(
                field_name=spec.field_ctx.name,
                field_type=spec.type,
                holder_class=spec.builder.cls,
                engine=deserialize_option,
            )
    field_indices: Iterable[Any]
    if as_dict:
        field_indices = zip((f"'{name}'" for name in fields), fields)
    else:
        field_indices = enumerate(fields)
    if not defaults:
        packed_value = spec.expression
    else:
        packed_value = "value"
    for idx, field in field_indices:
        unpacker = UnpackerRegistry.get(
            spec.copy(
                type=annotations.get(field, Any),
                expression=f"{packed_value}[{idx}]",
                could_be_none=True,
            )
        )
        unpackers.append(unpacker)

    if not defaults:
        return f"{type_name(spec.type)}({', '.join(unpackers)})"

    lines = CodeLines()
    method_name = (
        f"__unpack_named_tuple_{spec.builder.cls.__name__}_"
        f"{spec.field_ctx.name}__{str(uuid.uuid4().hex)}"
    )
    lines.append("@classmethod")
    default_kwargs = spec.builder.get_unpack_method_default_flag_values()
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
        lines.append(f"return {type_name(spec.type)}(*fields)")
    lines.append(f"setattr(cls, '{method_name}', {method_name})")
    if spec.builder.get_config().debug:
        print(f"{type_name(spec.builder.cls)}:")
        print(lines.as_text())
    exec(lines.as_text(), spec.builder.globals, spec.builder.__dict__)
    method_args = ", ".join(
        filter(None, (spec.expression, spec.builder.get_unpack_method_flags()))
    )
    return f"cls.{method_name}({method_args})"


def unpack_typed_dict(spec: ValueSpec) -> Expression:
    resolved = resolve_type_params(spec.origin_type, get_args(spec.type))[
        spec.origin_type
    ]
    annotations = {
        k: resolved.get(v, v)
        for k, v in spec.origin_type.__annotations__.items()
    }
    all_keys = list(annotations.keys())
    required_keys = getattr(spec.type, "__required_keys__", all_keys)
    optional_keys = getattr(spec.type, "__optional_keys__", [])
    lines = CodeLines()
    method_name = (
        f"__unpack_typed_dict_{spec.builder.cls.__name__}_"
        f"{spec.field_ctx.name}__{str(uuid.uuid4().hex)}"
    )
    default_kwargs = spec.builder.get_unpack_method_default_flag_values()
    lines.append("@classmethod")
    if default_kwargs:
        lines.append(f"def {method_name}(cls, value, {default_kwargs}):")
    else:
        lines.append(f"def {method_name}(cls, value):")
    with lines.indent():
        lines.append("d = {}")
        for key in sorted(required_keys, key=all_keys.index):
            unpacker = UnpackerRegistry.get(
                spec.copy(
                    type=annotations[key],
                    expression=f"value['{key}']",
                    could_be_none=True,
                )
            )
            lines.append(f"d['{key}'] = {unpacker}")
        for key in sorted(optional_keys, key=all_keys.index):
            lines.append(f"key_value = value.get('{key}', MISSING)")
            lines.append("if key_value is not MISSING:")
            with lines.indent():
                unpacker = UnpackerRegistry.get(
                    spec.copy(
                        type=annotations[key],
                        expression="key_value",
                        could_be_none=True,
                    )
                )
                lines.append(f"d['{key}'] = {unpacker}")
        lines.append("return d")
    lines.append(f"setattr(cls, '{method_name}', {method_name})")
    if spec.builder.get_config().debug:
        print(f"{type_name(spec.builder.cls)}:")
        print(lines.as_text())
    exec(lines.as_text(), spec.builder.globals, spec.builder.__dict__)
    method_args = ", ".join(
        filter(None, (spec.expression, spec.builder.get_unpack_method_flags()))
    )
    return f"cls.{method_name}({method_args})"


@register
def unpack_collection(spec: ValueSpec) -> Optional[Expression]:
    if not issubclass(spec.origin_type, typing.Collection):
        return None
    elif issubclass(spec.origin_type, enum.Enum):
        return None

    args = get_args(spec.type)

    def inner_expr(
        arg_num: int = 0, v_name: str = "value", v_type: Optional[Type] = None
    ) -> Expression:
        if v_type:
            return UnpackerRegistry.get(
                spec.copy(type=v_type, expression=v_name)
            )
        else:
            if args and len(args) > arg_num:
                type_arg: Any = args[arg_num]
            else:
                type_arg = Any
            return UnpackerRegistry.get(
                spec.copy(
                    type=type_arg,
                    expression=v_name,
                    could_be_none=True,
                    field_ctx=spec.field_ctx.copy(metadata={}),
                )
            )

    if issubclass(spec.origin_type, typing.ByteString):
        if spec.origin_type is bytes:
            spec.builder.ensure_object_imported(decodebytes)
            return f"decodebytes({spec.expression}.encode())"
        elif spec.origin_type is bytearray:
            spec.builder.ensure_object_imported(decodebytes)
            return f"bytearray(decodebytes({spec.expression}.encode()))"
    elif issubclass(spec.origin_type, str):
        return spec.expression
    elif ensure_generic_collection_subclass(spec, List):
        return f"[{inner_expr()} for value in {spec.expression}]"
    elif ensure_generic_collection_subclass(spec, typing.Deque):
        spec.builder.ensure_module_imported(collections)
        return (
            f"collections.deque([{inner_expr()} "
            f"for value in {spec.expression}])"
        )
    elif issubclass(spec.origin_type, Tuple):  # type: ignore
        if is_named_tuple(spec.origin_type):
            return unpack_named_tuple(spec)
        elif ensure_generic_collection(spec):
            return unpack_tuple(spec, args)
    elif ensure_generic_collection_subclass(spec, typing.FrozenSet):
        return f"frozenset([{inner_expr()} for value in {spec.expression}])"
    elif ensure_generic_collection_subclass(spec, typing.AbstractSet):
        return f"set([{inner_expr()} for value in {spec.expression}])"
    elif ensure_generic_mapping(spec, args, typing.ChainMap):
        spec.builder.ensure_module_imported(collections)
        return (
            f'collections.ChainMap(*[{{{inner_expr(0, "key")}:{inner_expr(1)} '
            f"for key, value in m.items()}} for m in {spec.expression}])"
        )
    elif ensure_generic_mapping(spec, args, typing_extensions.OrderedDict):
        spec.builder.ensure_module_imported(collections)
        return (
            f'collections.OrderedDict({{{inner_expr(0, "key")}: '
            f"{inner_expr(1)} for key, value in {spec.expression}.items()}})"
        )
    elif ensure_generic_mapping(spec, args, typing.DefaultDict):
        spec.builder.ensure_module_imported(collections)
        default_type = type_name(args[1] if args else None)
        return (
            f"collections.defaultdict({default_type}, "
            f'{{{inner_expr(0, "key")}: '
            f"{inner_expr(1)} for key, value in {spec.expression}.items()}})"
        )
    elif ensure_generic_mapping(spec, args, typing.Counter):
        spec.builder.ensure_module_imported(collections)
        return (
            f'collections.Counter({{{inner_expr(0, "key")}: '
            f"{inner_expr(1, v_type=int)} "
            f"for key, value in {spec.expression}.items()}})"
        )
    elif is_typed_dict(spec.origin_type):
        return unpack_typed_dict(spec)
    elif ensure_generic_mapping(spec, args, typing.Mapping):
        return (
            f'{{{inner_expr(0, "key")}: {inner_expr(1)} '
            f"for key, value in {spec.expression}.items()}}"
        )
    elif ensure_generic_collection_subclass(spec, typing.Sequence):
        return f"[{inner_expr()} for value in {spec.expression}]"


@register
def unpack_pathlike(spec: ValueSpec) -> Optional[Expression]:
    if spec.origin_type is os.PathLike:
        spec.builder.ensure_module_imported(pathlib)
        return f"{type_name(pathlib.PurePath)}({spec.expression})"
    elif issubclass(spec.origin_type, os.PathLike):
        return f"{type_name(spec.origin_type)}({spec.expression})"


@register
def unpack_enum(spec: ValueSpec) -> Optional[Expression]:
    if issubclass(spec.origin_type, enum.Enum):
        return f"{type_name(spec.origin_type)}({spec.expression})"
