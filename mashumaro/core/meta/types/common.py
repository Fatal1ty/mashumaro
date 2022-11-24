import collections.abc
from dataclasses import dataclass, field, is_dataclass, replace
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Mapping,
    Optional,
    Tuple,
    Type,
)

from typing_extensions import TypeAlias

from mashumaro.core.const import PEP_585_COMPATIBLE
from mashumaro.core.meta.helpers import get_type_origin, is_generic, type_name
from mashumaro.exceptions import UnserializableDataError, UnserializableField

if TYPE_CHECKING:  # pragma no cover
    from mashumaro.core.meta.code.builder import CodeBuilder
else:
    CodeBuilder = Any


NoneType = type(None)
Expression: TypeAlias = str


PROPER_COLLECTION_TYPES: Dict[Type, str] = {
    tuple: "typing.Tuple[T]",
    list: "typing.List[T]",
    set: "typing.Set[T]",
    frozenset: "typing.FrozenSet[T]",
    dict: "typing.Dict[KT,VT] or Mapping[KT,VT]",
    collections.deque: "typing.Deque[T]",
    collections.ChainMap: "typing.ChainMap[KT,VT]",
    collections.OrderedDict: "typing.OrderedDict[KT,VT]",
    collections.Counter: "typing.Counter[KT]",
}


@dataclass
class FieldContext:
    name: str
    metadata: Mapping

    def copy(self, **changes) -> "FieldContext":
        return replace(self, **changes)


@dataclass
class ValueSpec:
    type: Type
    origin_type: Type = field(init=False)
    expression: Expression
    builder: CodeBuilder
    field_ctx: FieldContext
    could_be_none: bool = True

    def __setattr__(self, key, value):
        if key == "type":
            self.origin_type = get_type_origin(value)
        super().__setattr__(key, value)

    def copy(self, **changes) -> "ValueSpec":
        return replace(self, **changes)


ValueSpecExprCreator: TypeAlias = Callable[[ValueSpec], Optional[Expression]]


@dataclass
class Registry:
    _registry: List[ValueSpecExprCreator] = field(default_factory=list)

    def register(self, function: ValueSpecExprCreator) -> ValueSpecExprCreator:
        self._registry.append(function)
        return function

    def get(self, spec: ValueSpec) -> Expression:
        spec.type = spec.builder._get_real_type(spec.field_ctx.name, spec.type)
        for packer in self._registry:
            expr = packer(spec)
            if expr is not None:
                return expr
        raise UnserializableField(
            spec.field_ctx.name, spec.type, spec.builder.cls
        )


def ensure_generic_collection(spec: ValueSpec) -> bool:
    if not PEP_585_COMPATIBLE:
        proper_type = PROPER_COLLECTION_TYPES.get(spec.type)
        if proper_type:
            raise UnserializableField(
                field_name=spec.field_ctx.name,
                field_type=spec.type,
                holder_class=spec.builder.cls,
                msg=f"Use {proper_type} instead",
            )
    if not is_generic(spec.type):
        return False
    return True


def ensure_collection_arg_types_supported(
    collection_type: Type,
    arg_types: Tuple[Type, ...],
) -> bool:
    if arg_types and is_dataclass(arg_types[0]):
        raise UnserializableDataError(
            f"{type_name(collection_type, short=True)} "
            f"with dataclasses as keys is not supported by mashumaro"
        )
    return True


def ensure_generic_collection_subclass(
    spec: ValueSpec, *checked_types
) -> bool:
    return issubclass(
        spec.origin_type, checked_types
    ) and ensure_generic_collection(spec)


def ensure_generic_mapping(spec: ValueSpec, args, checked_type) -> bool:
    return ensure_generic_collection_subclass(
        spec, checked_type
    ) and ensure_collection_arg_types_supported(spec.origin_type, args)


def expr_or_maybe_none(spec: ValueSpec, new_expr: Expression) -> Expression:
    if spec.could_be_none:
        return f"{new_expr} if {spec.expression} is not None else None"
    else:
        return new_expr
