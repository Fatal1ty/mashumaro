---
title: Dialects
group: Customization
---

# Dialects

A dialect is a reusable serialization profile. It separates an external representation from the data model and can be selected as a model default, passed at call time, or supplied to a codec.

Typical uses include public versus legacy API shapes, database versus network representations, date formats by partner, compact versus readable named tuples, and format-native pass-through rules.

## Define a dialect

```python
from datetime import date, datetime

from mashumaro.dialect import Dialect


class ISOAPIDialect(Dialect):
    serialization_strategy = {
        date: {
            "serialize": date.isoformat,
            "deserialize": date.fromisoformat,
        }
    }
    serialize_by_alias = True
    omit_none = True


class OrdinalStorageDialect(Dialect):
    serialization_strategy = {
        date: {
            "serialize": date.toordinal,
            "deserialize": date.fromordinal,
        }
    }
    omit_none = False
```

Dialect attributes are class attributes. Pass dialect classes such as `ISOAPIDialect`, not instances.

The two date strategies above use the standard [`date.isoformat()`](https://docs.python.org/3/library/datetime.html#datetime.date.isoformat), [`date.fromisoformat()`](https://docs.python.org/3/library/datetime.html#datetime.date.fromisoformat), [`date.toordinal()`](https://docs.python.org/3/library/datetime.html#datetime.date.toordinal), and [`date.fromordinal()`](https://docs.python.org/3/library/datetime.html#datetime.date.fromordinal) representations.

## Supported options

| Option | Purpose |
|---|---|
| `serialization_strategy` | Type-to-strategy mapping |
| `serialize_by_alias` | Emit external alias names |
| `namedtuple_as_dict` | Represent named tuples as mappings |
| `omit_none` | Omit fields containing `None` |
| `omit_default` | Omit fields equal to defaults |
| `no_copy_collections` | Pass selected collection types through without copying |

The unset sentinel lets a model or another dialect layer supply a value. Explicit `False` is different from leaving an option unset.

## Fixed model default

Set `Config.dialect` when a dataclass always uses one representation:

```python
from dataclasses import dataclass
from datetime import date

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig


@dataclass
class Release(DataClassDictMixin):
    name: str
    day: date

    class Config(BaseConfig):
        dialect = OrdinalStorageDialect


release = Release("1.0", date(2024, 1, 1))
assert release.to_dict() == {"name": "1.0", "day": 738886}
```

A fixed dialect does not add a `dialect=` method parameter. It is compiled into the model's normal behavior.

## Select a dialect at call time

Enable `ADD_DIALECT_SUPPORT` to generate a keyword argument for `to_dict()` and `from_dict()` and the corresponding format mixin methods:

```python
from dataclasses import dataclass
from datetime import date

from mashumaro import DataClassDictMixin
from mashumaro.config import ADD_DIALECT_SUPPORT, BaseConfig


@dataclass
class Release(DataClassDictMixin):
    name: str
    day: date

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]


release = Release("1.0", date(2024, 1, 1))

assert release.to_dict(dialect=ISOAPIDialect) == {
    "name": "1.0",
    "day": "2024-01-01",
}
assert release.to_dict(dialect=OrdinalStorageDialect) == {
    "name": "1.0",
    "day": 738886,
}
```

If the model also defines `Config.dialect`, that class is the default when the call omits `dialect=`; the explicit call argument selects another profile.

Dynamic dialect support propagates through supported nested dataclasses, unions, typed dictionaries, named tuples, and generic shapes when their generated methods participate in dialect handling.

## Codec default dialect

Every reusable encoder and decoder accepts `default_dialect=`:

```python
from datetime import date

from mashumaro.codecs.json import JSONDecoder, JSONEncoder

encoder = JSONEncoder(
    list[date], default_dialect=OrdinalStorageDialect
)
decoder = JSONDecoder(
    list[date], default_dialect=OrdinalStorageDialect
)

payload = encoder.encode([date(2026, 8, 16)])
assert payload == "[739844]"
assert decoder.decode(payload) == [date(2026, 8, 16)]
```

Codec dialects are the cleanest way to customize a non-dataclass root shape.

## Built-in format dialects

Mashumaro uses dialects internally for format-native behavior:

| Dialect | Behavior |
|---|---|
| `OrjsonDialect` | Passes `datetime`, `date`, `time`, and `UUID` to [orjson](https://github.com/ijl/orjson); avoids copying lists/dicts |
| `TOMLDialect` | Passes native [TOML](https://toml.io/en/v1.0.0) date/time values, omits `None`, avoids copying lists/dicts |
| `MessagePackDialect` | Passes bytes/bytearray/memoryview/Buffer in [MessagePack](https://msgpack.org/) binary form, avoids copying lists/dicts |

When a TOML, MessagePack, or orjson codec receives `default_dialect=YourDialect`, the format dialect is merged with your custom dialect so required native behavior remains available.

## Merging dialects

`Dialect.merge(other)` creates a new dialect class. Serialization-strategy dictionaries are copied and overlaid; `other` wins for the same type/direction. This resembles a [dictionary union](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict) for strategy entries. `omit_none`, `omit_default`, and `no_copy_collections` also take the explicit value from `other`, falling back to the left-hand dialect when unset.

```python
class CompactDialect(Dialect):
    omit_none = True
    omit_default = True


CombinedDialect = ISOAPIDialect.merge(CompactDialect)
```

Current merge behavior is intentionally narrow: `serialize_by_alias` and `namedtuple_as_dict` are not copied by `Dialect.merge`. If a merged profile needs them, define them on the final dialect class explicitly.

```python
class CombinedDialect(ISOAPIDialect.merge(CompactDialect)):
    serialize_by_alias = True
    namedtuple_as_dict = True
```

## `no_copy_collections`

This option is a sequence of collection origins that may be returned unchanged when no element conversion is required:

```python
class FastInternalDialect(Dialect):
    no_copy_collections = (list, dict)
```

It can reduce allocations, but it changes isolation guarantees: a downstream encoder or hook may see the caller's mutable collection. Use it only for trusted internal pipelines and benchmark the actual workload. Built-in format dialects use it where their encoders can safely consume the native containers.

## Config versus dialect

Model config describes the model's default policy; a dialect describes a reusable external profile. An explicit model value can override a dialect default for options such as omission because “unset” and `False` are distinct.

Choose one source of truth per concern:

- Put invariant security behavior such as `forbid_extra_keys` in config; dialects do not define it.
- Put alias-output policy, omission, and type representations in a dialect when they vary by destination.
- Put an unchanging representation in config when the model has only one contract.
- Put a one-field exception in field metadata.

Keep invariant security behavior in model config. A caller-selectable dialect should not be able to weaken an input-validation boundary.

## Failure modes

- Passing a dialect instance instead of a class raises `BadDialect`.
- Passing `dialect=` without `ADD_DIALECT_SUPPORT` raises `TypeError` because the generated method has no such parameter.
- Pass-through rules inherited from a format dialect still depend on the final encoder's capabilities.
- A custom dialect used for serialization must define a compatible reverse rule if round trips are required.
- Aggressive `no_copy_collections` can leak mutations across a serialization boundary.
