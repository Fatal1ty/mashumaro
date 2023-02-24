from dataclasses import dataclass
from typing import Union


class Annotation:
    pass


class Constraint(Annotation):
    pass


@dataclass(unsafe_hash=True)
class Minimum(Constraint):
    value: Union[int, float]


@dataclass(unsafe_hash=True)
class ExclusiveMinimum(Constraint):
    value: Union[int, float]


@dataclass(unsafe_hash=True)
class Maximum(Constraint):
    value: Union[int, float]


@dataclass(unsafe_hash=True)
class ExclusiveMaximum(Constraint):
    value: Union[int, float]
