---
title: Supported Types
---

# Supported Types

Mashumaro supports [dataclasses](https://docs.python.org/3/library/dataclasses.html), standard collections, modern [typing constructs](https://docs.python.org/3/library/typing.html), enums, date/time objects, slices, paths, network addresses, decimals, UUIDs, patterns, and user-defined extensions. Support applies recursively: a type can appear at the root of a codec, as a dataclass field, inside a collection, or as a type argument of another supported generic.

This chapter describes the **default basic representation**. A format-specific dialect may keep selected native values — notably bytes in MessagePack, date/time values in TOML, and several scalars in orjson.

## Representation reference

### Scalars and special values

| Python type | Basic serialized form | Deserialization behavior |
|---|---|---|
| `None` / `NoneType` | `None` | Produces `None` |
| `str` | `str` | Calls `str` conversion where needed |
| `int` | `int` | Calls `int` conversion and wraps failure |
| `float` | `float` | Calls `float` conversion and wraps failure |
| `bool` | `bool` | Calls `bool` conversion |
| `bytes` | Base64 ASCII `str` | Base64-decodes to `bytes` |
| `bytearray` | Base64 ASCII `str` | Base64-decodes to `bytearray` |
| `Any` | Passed through | Passed through without typed conversion |

The default bytes encoder uses [`base64.encodebytes`](https://docs.python.org/3/library/base64.html#base64.encodebytes), whose output includes a trailing newline:

```python
from dataclasses import dataclass

from mashumaro import DataClassDictMixin


@dataclass
class Payload(DataClassDictMixin):
    body: bytes
    mutable_body: bytearray


payload = Payload(b"123", bytearray(b"123"))
assert payload.to_dict() == {
    "body": "MTIz\n",
    "mutable_body": "MTIz\n",
}
assert Payload.from_dict(payload.to_dict()) == payload
```

MessagePack overrides this basic behavior and stores binary values natively. For URL-safe or newline-free Base64 JSON, define a [SerializationStrategy](#/docs/serializationstrategy).

### Date and time

| Python type | Basic serialized form | Default constructor/parsing rule |
|---|---|---|
| [`datetime.datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime) | ISO 8601 `str` | [`datetime.fromisoformat`](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat) |
| [`datetime.date`](https://docs.python.org/3/library/datetime.html#datetime.date) | ISO 8601 `str` | [`date.fromisoformat`](https://docs.python.org/3/library/datetime.html#datetime.date.fromisoformat) |
| [`datetime.time`](https://docs.python.org/3/library/datetime.html#datetime.time) | ISO 8601 `str` | [`time.fromisoformat`](https://docs.python.org/3/library/datetime.html#datetime.time.fromisoformat) |
| [`datetime.timedelta`](https://docs.python.org/3/library/datetime.html#datetime.timedelta) | Total seconds as `float` | `timedelta(seconds=value)` |
| [`datetime.timezone`](https://docs.python.org/3/library/datetime.html#datetime.timezone) | `tzname(None)` string | Parses `UTC` or a `UTC±HH:MM` offset |
| [`zoneinfo.ZoneInfo`](https://docs.python.org/3/library/zoneinfo.html#zoneinfo.ZoneInfo) | IANA zone key as `str` | `ZoneInfo(value)` |

```python
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from mashumaro import DataClassDictMixin


@dataclass
class Schedule(DataClassDictMixin):
    starts_at: datetime
    day: date
    local_time: time
    timeout: timedelta
    fixed_zone: timezone
    named_zone: ZoneInfo


schedule = Schedule(
    starts_at=datetime(2026, 8, 16, 9, 30, 15, 123456),
    day=date(2026, 8, 16),
    local_time=time(9, 30),
    timeout=timedelta(seconds=2.5),
    fixed_zone=timezone.utc,
    named_zone=ZoneInfo("Europe/Belgrade"),
)

assert schedule.to_dict() == {
    "starts_at": "2026-08-16T09:30:15.123456",
    "day": "2026-08-16",
    "local_time": "09:30:00",
    "timeout": 2.5,
    "fixed_zone": "UTC",
    "named_zone": "Europe/Belgrade",
}
```

Field deserialization can also use the optional [`ciso8601`](https://pypi.org/project/ciso8601/) or [`pendulum`](https://pendulum.eustace.io/docs/#parsing) engine. See [Field Options](#/docs/field-options#datetime-parser-engines).

### Numeric and identifier types

| Python type | Basic serialized form | Example |
|---|---|---|
| [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html#decimal.Decimal) | `str` | `Decimal("1.330")` → `"1.330"` |
| [`fractions.Fraction`](https://docs.python.org/3/library/fractions.html#fractions.Fraction) | `str` | `Fraction(1, 3)` → `"1/3"` |
| [`uuid.UUID`](https://docs.python.org/3/library/uuid.html#uuid.UUID) | Canonical `str` | `"3c25dd74-f208-46a2-9606-dd3919e975b7"` |

String representations preserve decimal precision and the exact fraction value across JSON-compatible formats. `RoundedDecimal` is a built-in strategy for applying decimal quantization at serialization time.

```python
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

from mashumaro import DataClassDictMixin, field_options
from mashumaro.types import RoundedDecimal


@dataclass
class Price(DataClassDictMixin):
    amount: Decimal = field(
        metadata=field_options(
            serialization_strategy=RoundedDecimal(
                places=2, rounding=ROUND_HALF_UP
            )
        )
    )


assert Price(Decimal("10.235")).to_dict() == {"amount": "10.24"}
```

### IP addresses and networks

The complete [`ipaddress`](https://docs.python.org/3/library/ipaddress.html) family is represented as strings:

- `IPv4Address` and `IPv6Address`
- `IPv4Network` and `IPv6Network`
- `IPv4Interface` and `IPv6Interface`

```python
from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Network

from mashumaro import DataClassDictMixin


@dataclass
class NetworkRule(DataClassDictMixin):
    gateway: IPv4Address
    destination: IPv6Network


rule = NetworkRule(
    gateway=IPv4Address("192.168.1.1"),
    destination=IPv6Network("2001:db8::/32"),
)
assert NetworkRule.from_dict(rule.to_dict()) == rule
```

### Paths and patterns

Mashumaro supports [`pathlib.Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path), `PurePath`, `PosixPath`, `PurePosixPath`, `WindowsPath`, `PureWindowsPath`, custom subclasses, and [`os.PathLike`](https://docs.python.org/3/library/os.html#os.PathLike). Values are serialized with [`os.fspath()`](https://docs.python.org/3/library/os.html#os.fspath) and reconstructed according to the annotation and operating system.

[`re.Pattern`](https://docs.python.org/3/library/re.html#re.Pattern), `re.Pattern[str]`, `re.Pattern[bytes]`, and `typing.Pattern` serialize to their `.pattern` value and deserialize with [`re.compile`](https://docs.python.org/3/library/re.html#re.compile). String patterns produce strings; bytes patterns produce bytes.

### Slices

A [`slice`](https://docs.python.org/3/library/functions.html#slice) is serialized as a three-element list `[start, stop, step]`. Each component is an integer or `None`, matching the attributes of the `slice` object. Because the encoded form is a list, a `slice` cannot be used as a mapping key in JSON, TOML, YAML, or MessagePack.

```python
from dataclasses import dataclass

from mashumaro import DataClassDictMixin


@dataclass
class Window(DataClassDictMixin):
    rows: slice


assert Window(slice(0, 5, 2)).to_dict() == {"rows": [0, 5, 2]}
assert Window(slice(5)).to_dict() == {"rows": [None, 5, None]}
assert Window.from_dict({"rows": [1, 10, None]}) == Window(slice(1, 10))
```

## Collections

Collection contents are converted recursively. Abstract collection annotations deserialize to a useful concrete implementation.

| Annotation family | Basic serialized form | Deserialized concrete form |
|---|---|---|
| `list[T]`, `typing.List[T]` | `list` | `list` |
| `tuple[...]`, `typing.Tuple[...]` | `list` | `tuple` |
| `set[T]`, `collections.abc.Set[T]` | `list` | `set` |
| `frozenset[T]` | `list` | `frozenset` |
| `collections.deque[T]` | `list` | `deque` |
| `Sequence[T]`, `MutableSequence[T]` | `list` | `list` |
| `dict[K, V]`, `Mapping[K, V]`, `MutableMapping[K, V]` | `dict` | `dict` |
| `OrderedDict[K, V]` | `dict` | `OrderedDict` |
| `defaultdict[K, V]` | `dict` | `defaultdict` |
| `Counter[K]` | `dict` | `Counter` |
| `ChainMap[K, V]` | List of maps | `ChainMap` |
| `types.MappingProxyType[K, V]` | `dict` | Read-only mapping proxy |

Both legacy names from `typing` and [PEP 585](https://peps.python.org/pep-0585/) built-in generic syntax are supported. On supported Python versions, prefer `list[int]` and `dict[str, User]` unless your project needs a compatibility style.

### Tuples

Fixed, variable, and empty tuple shapes retain their typed meaning even though their basic representation is a list:

```python
from dataclasses import dataclass

from mashumaro import DataClassDictMixin


@dataclass
class TupleShapes(DataClassDictMixin):
    point: tuple[int, int]
    labels: tuple[str, ...]
    empty: tuple[()]


value = TupleShapes((10, 20), ("a", "b"), ())
assert value.to_dict() == {
    "point": [10, 20],
    "labels": ["a", "b"],
    "empty": [],
}
assert TupleShapes.from_dict(value.to_dict()) == value
```

Variadic tuple shapes based on `TypeVarTuple` and `Unpack` are supported; see [Generics and Modern Typing](#/docs/generics-and-modern-typing#variadic-generics-pep-646).

### Mapping keys

The basic codec can convert typed mapping keys recursively, but the final format still sets the wire constraint:

- JSON object keys are strings.
- TOML keys are strings.
- YAML and MessagePack can represent more key types, but downstream consumers may not.
- `slice` is encoded as a list, so it cannot be a mapping key in any of these formats.

For an interoperable JSON/TOML contract, prefer `dict[str, V]` or define a strategy that turns keys into an unambiguous string.

### Copy behavior

Collections are normally copied while their elements are converted. A dialect's `no_copy_collections` option can pass selected collection types through when it is safe. Built-in format dialects use this for some native containers; custom use is an optimization that can expose mutable input objects to the downstream encoder.

## Dataclasses

Nested dataclasses are supported even if only the root class inherits a mixin:

```python
from dataclasses import dataclass

from mashumaro import DataClassDictMixin


@dataclass
class CPU:
    cores: int


@dataclass
class Machine(DataClassDictMixin):
    name: str
    cpu: CPU
    replicas: list[CPU]


machine = Machine("builder", CPU(12), [CPU(4), CPU(8)])
assert Machine.from_dict(machine.to_dict()) == machine
```

Supported dataclass features include inheritance, [`slots=True` and `kw_only=True`](https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass), defaults, default factories, forward references, recursive models, generic dataclasses, `ClassVar`, `InitVar`, and `typing.Self`.

`ClassVar` is not an instance field and is ignored. `InitVar` participates in construction rather than stored output, following dataclass semantics.

## Named tuples

Typed and untyped [named tuples](https://docs.python.org/3/library/typing.html#typing.NamedTuple) are supported, including defaults and generic named tuples. The default representation is a list. Set `namedtuple_as_dict = True` globally, use a dialect, or select `as_dict` for one field.

```python
from dataclasses import dataclass, field
from typing import NamedTuple

from mashumaro import DataClassDictMixin


class Point(NamedTuple):
    x: int
    y: int = 0


@dataclass
class Shapes(DataClassDictMixin):
    compact: Point
    readable: Point = field(
        metadata={"serialize": "as_dict", "deserialize": "as_dict"}
    )


value = Shapes(Point(1, 2), Point(3, 4))
assert value.to_dict() == {
    "compact": [1, 2],
    "readable": {"x": 3, "y": 4},
}
```

When dictionary representation is enabled, missing named-tuple items with defaults use those defaults during deserialization.

## Typed dictionaries

[`TypedDict`](https://docs.python.org/3/library/typing.html#typing.TypedDict) can be a field type or codec root. Mashumaro understands total and non-total dictionaries, `Required`, `NotRequired`, and `ReadOnly` markers from both `typing` and [`typing_extensions`](https://typing-extensions.readthedocs.io/en/stable/).

```python
from typing import NotRequired, TypedDict

from mashumaro.codecs.basic import BasicDecoder, BasicEncoder


class Patch(TypedDict):
    user_id: int
    display_name: NotRequired[str]


decoder = BasicDecoder(Patch)
encoder = BasicEncoder(Patch)

patch = decoder.decode({"user_id": "42"})
assert patch == {"user_id": 42}
assert encoder.encode(patch) == {"user_id": 42}
```

On Python 3.10, import `NotRequired`, `Required`, and `ReadOnly` from `typing_extensions`.

## Enums and literals

Mashumaro supports [`Enum`, `IntEnum`, `StrEnum`, `Flag`, and `IntFlag`](https://docs.python.org/3/library/enum.html). The default serialized value is `.value`, and deserialization calls the enum type with that value.

```python
from dataclasses import dataclass
from enum import Enum
from typing import Literal

from mashumaro import DataClassDictMixin


class Status(Enum):
    OPEN = "open"
    CLOSED = "closed"


@dataclass
class Ticket(DataClassDictMixin):
    status: Status
    priority: Literal["low", "high"]


ticket = Ticket.from_dict({"status": "open", "priority": "high"})
assert ticket == Ticket(Status.OPEN, "high")
assert ticket.to_dict() == {"status": "open", "priority": "high"}
```

[`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) supports strings, integers, booleans, `None`, bytes, and enum members. A value outside the allowed literal set causes `InvalidFieldValue`.

To encode all enum subclasses by name instead of by value, register a strategy with `match_subclasses=True`.

## Optional and union types

Both `typing.Optional[T]`/`typing.Union[A, B]` and [PEP 604](https://peps.python.org/pep-0604/) `T | None`/`A | B` are supported. Recursive unions and unions nested inside collections are supported as well.

```python
from dataclasses import dataclass

from mashumaro import DataClassDictMixin


@dataclass
class Success:
    value: int


@dataclass
class Failure:
    error: str


@dataclass
class Response(DataClassDictMixin):
    result: Success | Failure | None
```

An untagged union can be ambiguous when variants accept the same representation — for example `bool | int` or multiple dataclasses with overlapping fields. Use [Discriminator](#/docs/discriminator) for a stable polymorphic wire contract.

## Other typing constructs

### `Annotated`

The underlying type is serialized normally. Mashumaro-specific metadata such as `Alias` and `Discriminator`, plus JSON Schema annotations, can be attached with [`Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated) without replacing the type:

```python
from dataclasses import dataclass
from typing import Annotated

from mashumaro import DataClassDictMixin
from mashumaro.types import Alias


@dataclass
class User(DataClassDictMixin):
    user_id: Annotated[int, Alias("userId")]
```

### `NewType`

A [`NewType`](https://docs.python.org/3/library/typing.html#typing.NewType) is serialized using its underlying supertype while keeping the declared shape for type analysis.

```python
from typing import NewType

UserId = NewType("UserId", int)
```

### `TypeVar` and bounds

[Type variables](https://docs.python.org/3/library/typing.html#typing.TypeVar) are resolved from a concrete generic use. Unbound variables fall back to their bound, constraint, default, or `Any` as appropriate. TypeVar defaults from [PEP 696](https://peps.python.org/pep-0696/) are supported through `typing_extensions` and natively on newer Python versions.

### `Final`, `LiteralString`, `Self`, and `ReadOnly`

These markers are supported from `typing` where available and from `typing_extensions` otherwise. They refine static meaning while Mashumaro converts the underlying runtime value.

### PEP 695 type aliases

On Python 3.12+, the [PEP 695 `type` statement](https://peps.python.org/pep-0695/) is supported as a codec shape or field annotation, including parameterized and recursive aliases:

```python
type JSONValue = (
    None | bool | int | float | str | list[JSONValue] | dict[str, JSONValue]
)
```

Recursive aliases are guarded during generated-code and JSON Schema construction.

## Python version guide

The package supports Python {{PYTHON_VERSION_RANGE}}. Many newer typing objects can be used on older supported interpreters through the mandatory `typing_extensions` dependency, but new grammar cannot be backported.

| Feature | Native Python | Earlier supported Python |
|---|---|---|
| `A | B` union syntax, `list[int]` | 3.10 | All supported versions already have it |
| `Required`, `NotRequired` | 3.11 | Import from `typing_extensions` on 3.10 |
| `Self` | 3.11 | Import from `typing_extensions` |
| `TypeVarTuple`, `Unpack` | 3.11 | Import from `typing_extensions` |
| PEP 695 `class Box[T]` and `type Alias = ...` syntax | 3.12 | No syntax backport; use `Generic` and assignment aliases |
| TypeVar defaults (PEP 696) | 3.13 | Use `typing_extensions.TypeVar(default=...)` |
| `ReadOnly` for `TypedDict` | 3.13 | Import from `typing_extensions` |
| Deferred annotation evaluation model | 3.14 | Use string references or `from __future__ import annotations` |

### Generic syntax by Python version

The following two definitions express the same model.

Python 3.10 and 3.11:

```python
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class Box(Generic[T]):
    value: T
```

Python 3.12 and newer:

```python
from dataclasses import dataclass


@dataclass
class Box[T]:
    value: T
```

Both forms work as `Box[date]` fields and codec roots. See [Generics and Modern Typing](#/docs/generics-and-modern-typing) for inheritance, variadic generics, forward references, and generic extension types.

## Format-specific representation differences

| Type | Basic/JSON/YAML default | orjson default | TOML default | MessagePack default |
|---|---|---|---|---|
| `bytes` | Base64 string | Base64 string | Base64 string | Native binary |
| `bytearray` | Base64 string | Base64 string | Base64 string | Native binary, restored as `bytearray` |
| `datetime` | ISO string | Passed to orjson | Native TOML datetime | ISO string |
| `date` | ISO string | Passed to orjson | Native TOML date | ISO string |
| `time` | ISO string | Passed to orjson | Native TOML time | ISO string |
| `UUID` | String | Passed to orjson | String | String |
| `None` field | Present unless omitted by config | Present unless omitted | Omitted by TOML dialect | Present unless omitted |

Format behavior is implemented with dialects, so you can merge it with your own representation rules instead of reimplementing the format integration.

## Custom and third-party types

An arbitrary class is not serialized by guessing its `__dict__`. Choose an explicit extension mechanism:

| Situation | Recommended mechanism |
|---|---|
| You own the class | [SerializableType](#/docs/serializabletype) |
| You own a generic class and want annotated conversion | `SerializableType` with `use_annotations=True` |
| You cannot modify the class | [SerializationStrategy](#/docs/serializationstrategy) |
| Only one field differs | Callable or strategy in [Field Options](#/docs/field-options) |
| The representation changes by API/format | [Dialect](#/docs/dialects) |
| Raw object must pass unchanged | `pass_through`, only when the final encoder accepts it |

Keeping the conversion explicit makes the wire representation reviewable, testable, and compatible with JSON Schema generation.
