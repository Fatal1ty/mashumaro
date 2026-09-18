---
title: SerializationStrategy
group: Customization
---

# SerializationStrategy

A `SerializationStrategy` adds or overrides conversion for a type without modifying that type. It is the main extension point for third-party classes, alternate scalar formats, and reusable organization-wide representation rules.

Strategies can be attached to one field, registered by type in a model `Config`, or packaged in a switchable dialect.

## A reusable strategy

```python
from dataclasses import dataclass, field
from datetime import datetime

from mashumaro import DataClassDictMixin, field_options
from mashumaro.types import SerializationStrategy


class FormattedDateTime(SerializationStrategy):
    def __init__(self, fmt: str):
        self.fmt = fmt

    def serialize(self, value: datetime) -> str:
        return value.strftime(self.fmt)

    def deserialize(self, value: str) -> datetime:
        return datetime.strptime(value, self.fmt)


@dataclass
class Report(DataClassDictMixin):
    short_time: datetime = field(
        metadata=field_options(
            serialization_strategy=FormattedDateTime("%Y%m%d")
        )
    )
    readable_time: datetime = field(
        metadata=field_options(
            serialization_strategy=FormattedDateTime("%d %B %Y")
        )
    )


report = Report(
    short_time=datetime(2026, 8, 16),
    readable_time=datetime(2026, 8, 16),
)
assert report.to_dict() == {
    "short_time": "20260816",
    "readable_time": "16 August 2026",
}
```

The strategy instance can hold configuration, which makes one implementation reusable for multiple fields. Python documents the directives accepted by `strftime()` and `strptime()` in its [format-code reference](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes).

## Register by type in `Config`

Register a strategy once when every field of a type should use it:

```python
from dataclasses import dataclass
from datetime import datetime

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig


@dataclass
class AuditEvent(DataClassDictMixin):
    created_at: datetime
    processed_at: datetime

    class Config(BaseConfig):
        serialization_strategy = {
            datetime: FormattedDateTime("%Y-%m-%d %H:%M:%S"),
        }
```

The mapping key is the target Python type. A field-level `serialization_strategy` is the more local rule and should be used when one field differs from the model convention.

## Dictionary form

You do not have to define a strategy class. A config or dialect entry may contain `serialize` and `deserialize` callables:

```python
from dataclasses import dataclass
from uuid import UUID

from mashumaro import DataClassDictMixin


@dataclass
class BinaryId(DataClassDictMixin):
    value: UUID

    class Config:
        serialization_strategy = {
            UUID: {
                "serialize": lambda value: value.hex,
                "deserialize": UUID,
            }
        }


item = BinaryId(UUID("20f16666-90f3-4d73-a034-4e73a57e8f30"))
assert item.to_dict() == {
    "value": "20f1666690f34d73a0344e73a57e8f30"
}
```

Entries may define only one direction. The missing direction falls back to normal handling where that is meaningful. The [`UUID.hex`](https://docs.python.org/3/library/uuid.html#uuid.UUID.hex) attribute used above produces the 32-character form without hyphens. For a stable round-trip contract, define and test both directions.

## Annotation-aware strategies

With `use_annotations=True`, Mashumaro converts according to the `deserialize()` parameter annotation before calling the method, and converts the `serialize()` result according to its return annotation afterward.

```python
from datetime import datetime, timezone

from mashumaro.types import SerializationStrategy


class UnixTimestamp(
    SerializationStrategy, use_annotations=True
):
    def serialize(self, value: datetime) -> float:
        return value.timestamp()

    def deserialize(self, value: float) -> datetime:
        return datetime.fromtimestamp(value, tz=timezone.utc)
```

As a result, an input string such as `"1723800000"` is converted to `float` before `deserialize()` runs. The return annotation also lets JSON Schema describe the serialized type as a number.

Annotation processing changes the boundary of your method. Without it, the method sees raw input and its return value is final. With it, Mashumaro applies recursive typed conversion on both sides.

## Match subclasses

By default a strategy registered for `Base` matches exactly `Base`. Opt into subclass matching when a base-class policy should apply across a hierarchy:

```python
from dataclasses import dataclass
from enum import Enum

from mashumaro import DataClassDictMixin
from mashumaro.types import SerializationStrategy


class EnumByName(
    SerializationStrategy, match_subclasses=True
):
    def serialize(self, value: Enum) -> str:
        return value.name

    def deserialize(self, value: str) -> Enum:
        raise NotImplementedError


class Color(Enum):
    RED = "#f00"
    BLUE = "#00f"


@dataclass
class Theme(DataClassDictMixin):
    color: Color

    class Config:
        serialization_strategy = {Enum: EnumByName()}


assert Theme(Color.RED).to_dict() == {"color": "RED"}
```

When more than one registered base type matches, Mashumaro follows the target type's [method-resolution order](https://docs.python.org/3/tutorial/classes.html#multiple-inheritance) and uses the first registered match. Register narrow rules when multiple hierarchies could overlap.

Deserialization by a generic base such as `Enum` cannot know the concrete subclass from only the base strategy method. The generated field still knows `Color`, but the example intentionally leaves deserialization undefined to emphasize that each direction needs a real policy.

## Generic third-party types

A strategy can itself be generic. Register it under the target origin type; Mashumaro substitutes the field's concrete type arguments into the strategy annotations. The example uses the third-party [`multidict.MultiDict`](https://multidict.aio-libs.org/en/stable/multidict/) container.

```python
from dataclasses import dataclass
from datetime import date
from typing import Generic, TypeVar

from multidict import MultiDict

from mashumaro import DataClassDictMixin
from mashumaro.types import SerializationStrategy

T = TypeVar("T")


class MultiDictStrategy(SerializationStrategy, Generic[T]):
    def serialize(self, value: MultiDict[T]) -> list[tuple[str, T]]:
        return list(value.items())

    def deserialize(
        self, value: list[tuple[str, T]]
    ) -> MultiDict[T]:
        return MultiDict(value)


@dataclass
class Query(DataClassDictMixin):
    dates: MultiDict[date]

    class Config:
        serialization_strategy = {MultiDict: MultiDictStrategy()}
```

Generic strategies use their annotations implicitly; there is no need to pass `use_annotations=True`. The number and order of strategy type variables must match the target generic type.

## Built-in `RoundedDecimal`

`RoundedDecimal(places=None, rounding=None)` serializes a [`Decimal`](https://docs.python.org/3/library/decimal.html#decimal.Decimal) to a string and optionally [quantizes](https://docs.python.org/3/library/decimal.html#decimal.Decimal.quantize) it first. Deserialization constructs a `Decimal` from the incoming value.

```python
from decimal import Decimal, ROUND_DOWN

from mashumaro.types import RoundedDecimal

money_strategy = RoundedDecimal(places=2, rounding=ROUND_DOWN)
assert money_strategy.serialize(Decimal("12.349")) == "12.34"
```

Attach it per field when different currencies or measurements use different scales, or register it for `Decimal` when the rule is model-wide.

## `pass_through`

`mashumaro.pass_through` is a strategy whose two directions return the input unchanged:

```python
from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin, pass_through


@dataclass
class Envelope(DataClassDictMixin):
    raw: object = field(
        metadata={
            "serialize": pass_through,
            "deserialize": pass_through,
        }
    )
```

It is safe only when the next layer accepts the raw value. MessagePack can accept bytes; standard JSON cannot encode an arbitrary object. Pass-through also skips normal reconstruction, so use it deliberately at trusted boundaries.

## Strategies and dialects

Put a strategy in a dialect when the same Python model needs different external representations:

```python
from datetime import datetime

from mashumaro.dialect import Dialect


class PublicAPIDialect(Dialect):
    serialization_strategy = {
        datetime: FormattedDateTime("%Y-%m-%dT%H:%M:%S"),
    }


class LegacyAPIDialect(Dialect):
    serialization_strategy = {
        datetime: FormattedDateTime("%d/%m/%Y %H:%M:%S"),
    }
```

See [Dialects](#/docs/dialects) for default, call-time, and codec usage.

## Precedence and design rules

- A field-specific strategy is the narrowest and clearest override.
- A model config expresses one model family's stable default.
- A dialect expresses an external representation that may be selected or reused.
- Built-in type behavior is used only when no applicable override replaces it.
- Method annotations affect annotation-aware runtime conversion and JSON Schema output.

Avoid strategies that depend on unrelated global state. Immutable strategy objects with explicit constructor settings are easier to cache, test, and reason about.
