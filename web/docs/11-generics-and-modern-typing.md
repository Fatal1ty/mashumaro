---
title: Generics and Modern Typing
group: Advanced
---

# Generics and Modern Typing

Mashumaro resolves [type variables](https://docs.python.org/3/library/typing.html#typing.TypeVar) through generic dataclass inheritance, parameterized fields, codecs, serialization strategies, and custom serializable types. It supports classic [`Generic`](https://docs.python.org/3/library/typing.html#typing.Generic), [PEP 646](https://peps.python.org/pep-0646/) variadic generics, [PEP 695](https://peps.python.org/pep-0695/) syntax and type aliases, [PEP 696](https://peps.python.org/pep-0696/) TypeVar defaults, and recursive generic models.

## Parameterized field types

The most common pattern is a generic dataclass used with different concrete arguments:

```python
from dataclasses import dataclass
from datetime import date
from typing import Generic, TypeVar

from mashumaro import DataClassDictMixin

T = TypeVar("T")


@dataclass
class Box(Generic[T]):
    value: T


@dataclass
class Document(DataClassDictMixin):
    published: Box[date]
    title: Box[str]


raw = {
    "published": {"value": "2026-05-26"},
    "title": {"value": "Mashumaro"},
}
document = Document.from_dict(raw)

assert document.published.value == date(2026, 5, 26)
assert document.title.value == "Mashumaro"
assert document.to_dict() == raw
```

The generic dataclass itself does not need a mixin when it is nested. For direct typed methods, create a concrete subclass such as `DateBox(Box[date], DataClassDictMixin)`; calling an origin method through `Box[date]` does not specialize that generated method at runtime.

## Concrete generic inheritance

Subclass a generic dataclass to create a named concrete model:

```python
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import Generic, TypeVar

from mashumaro import DataClassDictMixin

K = TypeVar("K")
V = TypeVar("V")


@dataclass
class Index(Generic[K, V]):
    entries: Mapping[K, V]


@dataclass
class ReleaseIndex(Index[str, date], DataClassDictMixin):
    pass


index = ReleaseIndex.from_dict(
    {"entries": {"stable": "2026-05-26"}}
)
assert index.entries["stable"] == date(2026, 5, 26)
```

Partial specialization and replacing a parent TypeVar with another TypeVar are supported. Unresolved variables use a bound, constraints, a default, or `Any` depending on the declaration.

## Bounds, constraints, and defaults

```python
from dataclasses import dataclass
from datetime import date
from typing import Generic, TypeVar

BoundDate = TypeVar("BoundDate", bound=date)
DateOrString = TypeVar("DateOrString", date, str)


@dataclass
class Bounded(Generic[BoundDate]):
    value: BoundDate


@dataclass
class Constrained(Generic[DateOrString]):
    value: DateOrString
```

PEP 696 defaults can provide a concrete fallback:

```python
from typing_extensions import TypeVar

T = TypeVar("T", default=int)
```

[`typing_extensions.TypeVar`](https://typing-extensions.readthedocs.io/en/stable/#typing_extensions.TypeVar) makes defaults available on all supported Python versions; Python 3.13+ also provides native syntax/API support.

## Variadic generics (PEP 646)

[`TypeVarTuple`](https://docs.python.org/3/library/typing.html#typing.TypeVarTuple) and [`Unpack`](https://docs.python.org/3/library/typing.html#typing.Unpack) allow a tuple shape to carry any number of type parameters:

```python
from dataclasses import dataclass
from typing import Generic
from typing_extensions import TypeVarTuple, Unpack

from mashumaro import DataClassDictMixin

Ts = TypeVarTuple("Ts")


@dataclass
class Row(Generic[Unpack[Ts]]):
    values: tuple[Unpack[Ts]]


@dataclass
class Table(DataClassDictMixin):
    row: Row[int, float, str]


table = Table.from_dict({"row": {"values": [1, 2.5, "ok"]}})
assert table.row.values == (1, 2.5, "ok")
```

On Python 3.11+, star-unpacking syntax such as `tuple[*Ts]` is also available. Mashumaro supports fixed items around an unpack, arbitrary-length tuple arguments, and empty variadic tuples where Python's type syntax permits them.

## PEP 695 syntax (Python 3.12+)

Python 3.12 can declare type parameters directly:

```python
from dataclasses import dataclass


@dataclass
class Box[T]:
    value: T


@dataclass
class Pair[K, V]:
    key: K
    value: V
```

These classes work in parameterized fields, concrete inheritance, codecs, annotation-aware `SerializableType`, and generic strategies just like classic `Generic` classes.

The grammar is Python 3.12-only; a library supporting Python 3.10/3.11 should keep PEP 695 declarations in version-specific modules or use classic syntax.

## PEP 695 type aliases

The `type` statement can define simple, generic, and recursive shape aliases:

```python
type UserMap = dict[str, int]
type Page[T] = list[T]
type JSONValue = (
    None | bool | int | float | str | list[JSONValue] | dict[str, JSONValue]
)
```

Aliases can be codec roots or dataclass field types:

```python
from mashumaro.codecs.basic import BasicDecoder, BasicEncoder

encoder = BasicEncoder(Page[date])
decoder = BasicDecoder(Page[date])
```

Mashumaro resolves parameterized aliases and guards direct, wrapped, and mutually recursive aliases from infinite recursion. JSON Schema definitions use stable alias names.

## Recursive generic models

Forward references and `Self` work with generic dataclasses:

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from mashumaro import DataClassDictMixin

T = TypeVar("T")


@dataclass
class Node(Generic[T]):
    value: T
    children: list[Node[T]]


@dataclass
class Tree(DataClassDictMixin):
    root: Node[int]


tree = Tree.from_dict(
    {
        "root": {
            "value": "1",
            "children": [{"value": "2", "children": []}],
        }
    }
)
assert tree.root.children[0].value == 2
```

With [postponed annotations](https://docs.python.org/3/library/__future__.html#future-annotations) enabled by default, compilation can wait until referenced types exist.

> [!IMPORTANT]
> Calling an inherited mixin method through a runtime generic alias such as `Node[int].from_dict(...)` does not specialize that method with `int`; Python forwards the attribute to the unspecialized origin class. Put the specialized type in a containing model, use `BasicDecoder(Node[int])`, or create a concrete subclass when direct methods are required.

## Generic `SerializableType`

For a generic class you own, `SerializableType(use_annotations=True)` substitutes concrete type arguments into `_serialize()` and `_deserialize()` annotations. This is usually more concise than inspecting type objects manually.

See [SerializableType](#/docs/serializabletype#generic-owned-types) for a complete `DictWrapper[K, V]` example.

## Generic `SerializationStrategy`

For a third-party generic, make the strategy generic and register it under the target origin:

```python
class Config:
    serialization_strategy = {
        ThirdPartyContainer: ThirdPartyContainerStrategy()
    }
```

Mashumaro maps field arguments such as `ThirdPartyContainer[date]` into the strategy's method annotations. See [SerializationStrategy](#/docs/serializationstrategy#generic-third-party-types).

## Generic codec roots

Codecs accept any fully parameterized shape:

```python
from datetime import date

from mashumaro.codecs.json import JSONDecoder, JSONEncoder

shape = dict[str, list[Box[date] | None]]
encoder = JSONEncoder(shape)
decoder = JSONDecoder(shape)
```

Construct and reuse one codec per concrete shape. A bare generic with unresolved parameters has less conversion information and may fall back to bounds/defaults/[`Any`](https://docs.python.org/3/library/typing.html#typing.Any).

## Version matrix

| Capability | Python 3.10 | 3.11 | 3.12 | 3.13–3.14 |
|---|---|---|---|---|
| Classic `Generic[T]` | Yes | Yes | Yes | Yes |
| `TypeVarTuple`/`Unpack` objects | `typing_extensions` | Native | Native | Native |
| `tuple[*Ts]` syntax | Limited; use `Unpack` | Yes | Yes | Yes |
| PEP 695 class/type-alias syntax | No | No | Yes | Yes |
| TypeVar defaults | `typing_extensions` | `typing_extensions` | `typing_extensions` | Native or extension |
| Deferred 3.14 annotations | Future import model | Future import model | Future import model | Native in 3.14 |

## Troubleshooting generics

- Parameterize the root shape: prefer `Box[date]` over bare `Box`.
- Keep strategy TypeVars aligned with the third-party generic's parameter order.
- Use `typing_extensions` imports for a source file shared with Python 3.10.
- Put Python 3.12-only grammar in a module that older interpreters never parse.
- Leave `allow_postponed_evaluation=True` for forward and recursive references.
- Inspect generated code with `Config.debug=True` when a TypeVar resolves to an unexpected fallback.
