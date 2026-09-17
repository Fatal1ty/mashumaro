---
title: Field Options
group: Customization
---

# Field Options

Field options customize one dataclass field. They live in [`dataclasses.field(metadata=...)`](https://docs.python.org/3/library/dataclasses.html#dataclasses.field), so they compose with defaults, factories, `init`, `repr`, and metadata used by other libraries. You provide the metadata mapping when declaring the field; after the field is created, dataclasses exposes it as a read-only mapping intended for third-party extensions. Mashumaro reads its options from that mapping.

Use field options for a local exception. If all fields of a type share a rule, move it to [Config Options](#/docs/config-options) or a [Dialect](#/docs/dialects).

## The `field_options` helper

```python
from dataclasses import dataclass, field
from datetime import datetime

from mashumaro import DataClassDictMixin, field_options


@dataclass
class Event(DataClassDictMixin):
    created_at: datetime = field(
        metadata=field_options(
            serialize=lambda value: value.timestamp(),
            deserialize=lambda value: datetime.fromtimestamp(float(value)),
            alias="createdAt",
        )
    )
```

`field_options()` returns a normal metadata dictionary. Its named parameters are:

| Option | Value | Purpose |
|---|---|---|
| `serialize` | Callable, engine name, or `pass_through` | Override packing |
| `deserialize` | Callable, engine name, or `pass_through` | Override unpacking |
| `serialization_strategy` | `SerializationStrategy` instance | Override both directions |
| `alias` | `str | Sequence[str]` | One external field name or ordered aliases |

Additional keyword arguments are copied into the result, which lets Mashumaro metadata coexist with schema descriptions or another library's metadata.

You may also write the dictionary directly:

```python
value: int = field(metadata={"alias": "externalValue"})
```

## Custom `serialize` callable

The callable receives the field value and returns its serialized representation:

```python
from dataclasses import dataclass, field
from datetime import datetime

from mashumaro import DataClassDictMixin


def datetime_to_millis(value: datetime) -> int:
    return int(value.timestamp() * 1000)


@dataclass
class LogEntry(DataClassDictMixin):
    at: datetime = field(metadata={"serialize": datetime_to_millis})
```

Add a return annotation when JSON Schema should reflect the overridden representation. Here the field schema becomes an integer rather than the default date-time string.

The paired deserializer is independent:

```python
def datetime_from_millis(value: int) -> datetime:
    return datetime.fromtimestamp(value / 1000)


@dataclass
class LogEntry(DataClassDictMixin):
    at: datetime = field(
        metadata={
            "serialize": datetime_to_millis,
            "deserialize": datetime_from_millis,
        }
    )
```

Without the matching deserializer, normal datetime parsing expects an ISO string and will not round-trip the integer representation.

## Custom `deserialize` callable

The callable receives the external field value and must return the field's runtime value:

```python
from dataclasses import dataclass, field
from decimal import Decimal

from mashumaro import DataClassDictMixin


@dataclass
class Payment(DataClassDictMixin):
    amount: Decimal = field(
        metadata={"deserialize": lambda value: Decimal(str(value))}
    )
```

Exceptions raised by field conversion are reported as `InvalidFieldValue` with the field name, annotated type, input value, and holder class. See [Errors and Troubleshooting](#/docs/errors-and-troubleshooting).

## Serialization engines

String engine names select optimized built-in behavior for a small set of types.

### Named tuple engines

For a [`NamedTuple`](https://docs.python.org/3/library/typing.html#typing.NamedTuple) field, both directions accept `as_list` and `as_dict`:

```python
from dataclasses import dataclass, field
from typing import NamedTuple

from mashumaro import DataClassDictMixin


class Point(NamedTuple):
    x: int
    y: int


@dataclass
class Drawing(DataClassDictMixin):
    compact: Point = field(
        metadata={"serialize": "as_list", "deserialize": "as_list"}
    )
    readable: Point = field(
        metadata={"serialize": "as_dict", "deserialize": "as_dict"}
    )
```

`as_list` is the default unless config or dialect enables `namedtuple_as_dict`. A field engine can override that broader default.

### Omit engine

Set `serialize="omit"` to exclude a field unconditionally:

```python
from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin


@dataclass
class Session(DataClassDictMixin):
    user_id: int
    internal_token: str = field(metadata={"serialize": "omit"})


assert Session(42, "secret").to_dict() == {"user_id": 42}
```

This changes serialization only. Deserialization behavior still follows the field definition, alias, and default. Use a default when omitted input must still construct the dataclass.

### Datetime parser engines

The `deserialize` option supports [`ciso8601`](https://pypi.org/project/ciso8601/) and [`pendulum`](https://pendulum.eustace.io/docs/#parsing) for `datetime`, `date`, and `time` fields:

```python
from dataclasses import dataclass, field
from datetime import datetime

from mashumaro import DataClassDictMixin


@dataclass
class Event(DataClassDictMixin):
    at: datetime = field(metadata={"deserialize": "ciso8601"})
```

Install the named third-party module yourself. If it is missing, Mashumaro raises `ThirdPartyModuleNotFoundError` identifying the dependency and field. These parser engines affect only deserialization; choose a matching serializer if you need a non-default output format.

## Per-field `SerializationStrategy`

A strategy keeps both directions and constructor options in one object:

```python
from dataclasses import dataclass, field
from datetime import datetime

from mashumaro import DataClassDictMixin, field_options
from mashumaro.types import SerializationStrategy


class EpochSeconds(SerializationStrategy):
    def serialize(self, value: datetime) -> float:
        return value.timestamp()

    def deserialize(self, value: float) -> datetime:
        return datetime.fromtimestamp(value)


@dataclass
class Event(DataClassDictMixin):
    at: datetime = field(
        metadata=field_options(serialization_strategy=EpochSeconds())
    )
```

See [SerializationStrategy](#/docs/serializationstrategy) for annotation-aware and generic strategies.

## Aliases

An alias is the external key expected during deserialization:

```python
from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin


@dataclass
class APIResponse(DataClassDictMixin):
    status_code: int = field(metadata={"alias": "statusCode"})
    error_message: str = field(metadata={"alias": "errorMessage"})


response = APIResponse.from_dict(
    {"statusCode": 200, "errorMessage": ""}
)
```

Aliases are used for input by default. Output keeps Python field names unless `serialize_by_alias=True`, a dynamic `by_alias=True` flag is enabled, or a dialect selects alias output.

```python
@dataclass
class AliasedAPIResponse(DataClassDictMixin):
    status_code: int = field(metadata={"alias": "statusCode"})
    error_message: str = field(metadata={"alias": "errorMessage"})

    class Config:
        serialize_by_alias = True


response = AliasedAPIResponse.from_dict(
    {"statusCode": 200, "errorMessage": ""}
)


assert response.to_dict() == {
    "statusCode": 200,
    "errorMessage": "",
}
```

### Multiple aliases

Pass an ordered sequence when a field must accept more than one external name:

```python
from mashumaro import field_options


@dataclass
class User(DataClassDictMixin):
    user_id: int = field(
        metadata=field_options(alias=["userId", "user_id", "UserID"])
    )

    class Config:
        serialize_by_alias = True


assert User.from_dict({"userId": 1}) == User(1)
assert User.from_dict({"user_id": 2}) == User(2)
assert User.from_dict({"UserID": 3}) == User(3)
assert User(4).to_dict() == {"userId": 4}
```

Aliases are tried in declaration order. If an input contains more than one of them, the first matching alias wins. The first alias is also the primary alias used when serializing by alias and as the property name in generated JSON Schema. An empty sequence uses the Python field name.

Set `allow_deserialization_not_by_alias=True` when the Python field name should also be accepted. It is tried after all declared aliases. With `forbid_extra_keys=True`, every declared alias and the optional Python field name count as expected keys.

### `Annotated` aliases

Aliases can stay next to the type with [`Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated) instead of in `field()` metadata. Repeat `Alias(...)` to declare multiple names; the first one is primary:

```python
from typing import Annotated

from mashumaro.types import Alias


@dataclass
class User(DataClassDictMixin):
    user_id: Annotated[int, Alias("userId"), Alias("UserID")]
```

Alias sources are not combined. Precedence is intentionally local:

- `field(metadata={"alias": ...})` wins.
- Otherwise `Annotated[..., Alias(...)]` wins.
- Otherwise `Config.aliases` supplies the model-wide alias.

This lets a field override an inherited naming convention without changing the base config.

## Pass values through unchanged

Use `pass_through` in either direction to skip generated conversion:

```python
from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin, pass_through


@dataclass
class CachedValue(DataClassDictMixin):
    payload: object = field(
        metadata={
            "serialize": pass_through,
            "deserialize": pass_through,
        }
    )
```

Pass-through does not make a value serializable by the final format. A raw custom object may be acceptable to a database adapter but will still fail in [`json.dumps`](https://docs.python.org/3/library/json.html#json.dumps). It also bypasses input conversion, so it should be used only where the caller already guarantees the runtime type.

## Defaults and omission

Field defaults are regular [dataclass defaults and default factories](https://docs.python.org/3/library/dataclasses.html#default-factory-functions). During deserialization, a missing input key uses `default` or `default_factory`; a required field without either raises `MissingField`.

Omission options have different meanings:

| Feature | Condition | Scope |
|---|---|---|
| `serialize="omit"` | Always | One field |
| `omit_none` | Current value is `None` | Config, dialect, or call flag |
| `omit_default` | Current value equals its default/factory result | Config or dialect |

Do not use omission to conceal a required external field. A receiver still needs a compatible default or migration rule.

## Common mistakes

- Defining only a serializer and expecting the new representation to round-trip.
- Using an alias and assuming output changes automatically.
- Using `pass_through` before a format encoder that cannot accept the object.
- Forgetting a return annotation when JSON Schema should see the overridden type.
- Selecting `ciso8601` or `pendulum` without installing it.
- Hiding a secret only with a post-serialization hook when `serialize="omit"` would make the policy explicit at the field.
