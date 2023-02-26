from dataclasses import dataclass
from numbers import Number
from typing import Union


class Annotation:
    pass


class Constraint(Annotation):
    pass


@dataclass(unsafe_hash=True)
class Minimum(Constraint):
    value: Number


@dataclass(unsafe_hash=True)
class ExclusiveMinimum(Constraint):
    value: Number


@dataclass(unsafe_hash=True)
class Maximum(Constraint):
    value: Number


@dataclass(unsafe_hash=True)
class ExclusiveMaximum(Constraint):
    value: Number
