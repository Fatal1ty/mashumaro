from dataclasses import dataclass

from mashumaro.jsonschema.models import Numeric


class Annotation:
    pass


class Constraint(Annotation):
    pass


@dataclass(unsafe_hash=True)
class Minimum(Constraint):
    value: Numeric


@dataclass(unsafe_hash=True)
class ExclusiveMinimum(Constraint):
    value: Numeric


@dataclass(unsafe_hash=True)
class Maximum(Constraint):
    value: Numeric


@dataclass(unsafe_hash=True)
class ExclusiveMaximum(Constraint):
    value: Numeric
