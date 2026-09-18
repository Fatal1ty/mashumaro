---
title: SerializableType
group: Customization
---

# SerializableType

Use `SerializableType` when you own a class and want the class itself to define its stable serialized representation. The contract is explicit: `_serialize()` returns the representation, and `_deserialize()` rebuilds an instance.

For a third-party class you cannot modify, use [SerializationStrategy](#/docs/serializationstrategy). For a representation that changes by external API, prefer a [Dialect](#/docs/dialects) so the domain type stays independent of one wire contract.

## Basic contract

```python
from dataclasses import dataclass

from mashumaro import DataClassDictMixin
from mashumaro.types import SerializableType


class Airport(SerializableType):
    def __init__(self, code: str, city: str):
        self.code = code
        self.city = city

    def _serialize(self):
        return [self.code, self.city]

    @classmethod
    def _deserialize(cls, value):
        return cls(*value)

    def __eq__(self, other):
        return isinstance(other, Airport) and (
            self.code, self.city
        ) == (other.code, other.city)


@dataclass
class Flight(DataClassDictMixin):
    origin: Airport
    destination: Airport


data = {
    "origin": ["BEG", "Belgrade"],
    "destination": ["NRT", "Tokyo"],
}
flight = Flight.from_dict(data)

assert flight.origin == Airport("BEG", "Belgrade")
assert flight.to_dict() == data
```

Without annotation processing, the value passed to `_deserialize()` is raw input and the value returned from `_serialize()` is accepted as the final basic representation. This is ideal when your methods perform the entire conversion themselves.

## Annotation-aware conversion

Set `use_annotations=True` when Mashumaro should recursively convert the [function annotations](https://docs.python.org/3/reference/compound_stmts.html#function-definitions) on the input of `_deserialize()` and the return of `_serialize()`.

```python
from dataclasses import dataclass
from datetime import date

from mashumaro import DataClassDictMixin
from mashumaro.types import SerializableType


@dataclass
class Stop:
    airport: str
    day: date


class Itinerary(SerializableType, use_annotations=True):
    def __init__(self, stops: list[Stop]):
        self.stops = stops

    def _serialize(self) -> list[Stop]:
        return self.stops

    @classmethod
    def _deserialize(cls, stops: list[Stop]) -> "Itinerary":
        return cls(stops)


@dataclass
class Trip(DataClassDictMixin):
    itinerary: Itinerary


trip = Trip.from_dict(
    {
        "itinerary": [
            {"airport": "BEG", "day": "2026-08-16"},
            {"airport": "NRT", "day": "2026-08-17"},
        ]
    }
)

assert trip.itinerary.stops[0].day == date(2026, 8, 16)
assert trip.to_dict()["itinerary"][1]["day"] == "2026-08-17"
```

Both annotations matter. The `_deserialize()` parameter tells Mashumaro how to unpack raw data before your method runs. The `_serialize()` return type tells it how to pack the value your method returns.

> [!IMPORTANT]
> `use_annotations` is intentionally opt-in for compatibility with older code. Missing annotations while it is enabled make the conversion contract incomplete; annotate both directions.

## Generic owned types

Annotation substitution works for classic [`Generic`](https://docs.python.org/3/library/typing.html#typing.Generic) classes, [PEP 695 generics](https://peps.python.org/pep-0695/) on Python 3.12+, and [variadic generics](https://peps.python.org/pep-0646/).

```python
from dataclasses import dataclass
from datetime import date
from typing import Generic, TypeVar

from mashumaro import DataClassDictMixin
from mashumaro.types import SerializableType

K = TypeVar("K")
V = TypeVar("V")


class DictWrapper(dict[K, V], SerializableType, use_annotations=True):
    def _serialize(self) -> dict[K, V]:
        return dict(self)

    @classmethod
    def _deserialize(cls, value: dict[K, V]) -> "DictWrapper[K, V]":
        return cls(value)


@dataclass
class Index(DataClassDictMixin):
    by_date: DictWrapper[date, str]
    dates: DictWrapper[str, date]


raw = {
    "by_date": {"2026-05-26": "release"},
    "dates": {"release": "2026-05-26"},
}
index = Index.from_dict(raw)

assert date(2026, 5, 26) in index.by_date
assert index.dates["release"] == date(2026, 5, 26)
assert index.to_dict() == raw
```

On Python 3.12+, the class header may be written as `class DictWrapper[K, V](dict[K, V], SerializableType, use_annotations=True):`.

## `GenericSerializableType`

`GenericSerializableType` is a lower-level alternative. Instead of having Mashumaro substitute method annotations, your methods receive a list of concrete type arguments.

```python
from datetime import date
from typing import Generic, TypeVar

from mashumaro.types import GenericSerializableType

T = TypeVar("T")


class LegacyBox(Generic[T], GenericSerializableType):
    def __init__(self, value):
        self.value = value

    def _serialize(self, types):
        item_type = types[0]
        if item_type is date:
            return self.value.isoformat()
        return self.value

    @classmethod
    def _deserialize(cls, value, types):
        item_type = types[0]
        if item_type is date:
            value = date.fromisoformat(value)
        return cls(value)
```

Prefer annotation-aware `SerializableType` for new code: it composes naturally with nested generic types and gives Mashumaro enough information for JSON Schema generation. Use `GenericSerializableType` when the concrete type objects themselves drive custom runtime logic.

## Dataclass types that implement the interface

A class may be both a dataclass and a `SerializableType`. Its explicit interface wins over ordinary dataclass field packing for uses of that type. This is useful when the in-memory field layout must not leak into the wire representation.

```python
from dataclasses import dataclass

from mashumaro.types import SerializableType


@dataclass
class Coordinate(SerializableType, use_annotations=True):
    latitude: float
    longitude: float

    def _serialize(self) -> tuple[float, float]:
        return self.latitude, self.longitude

    @classmethod
    def _deserialize(cls, value: tuple[float, float]) -> "Coordinate":
        return cls(*value)
```

## JSON Schema interaction

For annotation-aware classes, [JSON Schema](https://json-schema.org/specification) follows the `_serialize()` return annotation. Without a usable return annotation, the schema builder cannot reliably infer the external representation. This is one reason to annotate custom serialization even when runtime conversion would work without it.

## Design guidance

- Keep `_serialize()` deterministic and side-effect free.
- Make `_deserialize()` accept only the documented external shape.
- Version the representation deliberately; changing a list to a mapping is a wire breaking change.
- Use annotation-aware conversion when nested values should follow normal Mashumaro rules.
- Test round trips and exact basic output, not only object equality.
- Use a strategy or dialect instead when the representation belongs to a particular API rather than to the class itself.
