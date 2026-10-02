from dataclasses import dataclass

from mashumaro.jsonschema.models import JSONSchema, Number


class Annotation:
    pass


class Constraint(Annotation):
    pass


class NumberConstraint(Constraint):
    pass


@dataclass(unsafe_hash=True)
class Minimum(NumberConstraint):
    value: Number


@dataclass(unsafe_hash=True)
class Maximum(NumberConstraint):
    value: Number


@dataclass(unsafe_hash=True)
class ExclusiveMinimum(NumberConstraint):
    value: Number


@dataclass(unsafe_hash=True)
class ExclusiveMaximum(NumberConstraint):
    value: Number


@dataclass(unsafe_hash=True)
class MultipleOf(NumberConstraint):
    value: Number


class StringConstraint(Constraint):
    pass


@dataclass(unsafe_hash=True)
class MinLength(StringConstraint):
    value: int


@dataclass(unsafe_hash=True)
class MaxLength(StringConstraint):
    value: int


@dataclass(unsafe_hash=True)
class Pattern(StringConstraint):
    value: str


class ArrayConstraint(Constraint):
    pass


@dataclass(unsafe_hash=True)
class MinItems(ArrayConstraint):
    value: int


@dataclass(unsafe_hash=True)
class MaxItems(ArrayConstraint):
    value: int


@dataclass(unsafe_hash=True)
class UniqueItems(ArrayConstraint):
    value: bool


@dataclass(unsafe_hash=True)
class Contains(ArrayConstraint):
    value: JSONSchema


@dataclass(unsafe_hash=True)
class MinContains(ArrayConstraint):
    value: int


@dataclass(unsafe_hash=True)
class MaxContains(ArrayConstraint):
    value: int


class ObjectConstraint(Constraint):
    pass


@dataclass(unsafe_hash=True)
class MaxProperties(ObjectConstraint):
    value: int


@dataclass(unsafe_hash=True)
class MinProperties(ObjectConstraint):
    value: int


@dataclass
class DependentRequired(ObjectConstraint):
    value: dict[str, set[str]]


__all__ = [
    "Annotation",
    "Contains",
    "DependentRequired",
    "ExclusiveMaximum",
    "ExclusiveMinimum",
    "MaxContains",
    "MaxItems",
    "MaxLength",
    "MaxProperties",
    "Maximum",
    "MinContains",
    "MinItems",
    "MinLength",
    "MinProperties",
    "Minimum",
    "MultipleOf",
    "Pattern",
    "UniqueItems",
]
