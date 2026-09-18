---
title: Config Options
group: Customization
---

# Config Options

An inner `Config` class defines model-wide serialization behavior. Configuration follows normal [Python class inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance), so a project can create a base mixin and let individual dataclasses override only their exceptions.

> [!IMPORTANT]
> The class-level `discriminator` is the exception. The `Config` class remains accessible through normal Python inheritance, but merely inheriting it does not make every descendant a new polymorphic entry point. A descendant can explicitly opt in by defining its own `Config` that declares a discriminator or inherits one from another config class. See [Class-level discriminator](#/docs/discriminator#class-level-discriminator) for details.

```python
from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig


class APIModel(DataClassDictMixin):
    class Config(BaseConfig):
        forbid_extra_keys = True
        allow_deserialization_not_by_alias = True
```

Inheriting `BaseConfig` is recommended for discoverability, type checking, and documented defaults, though a plain nested class with recognized attributes also works.

## Complete option reference

| Option | Default | Effect |
|---|---|---|
| `debug` | `False` | Print generated source code |
| `code_generation_options` | `[]` | Add optional method parameters/features |
| `serialization_strategy` | `{}` | Type-to-strategy mapping |
| `aliases` | `{}` | Field names mapped to one alias or ordered aliases |
| `serialize_by_alias` | Unset | Emit aliases by default |
| `allow_deserialization_not_by_alias` | `False` | Accept Python names for aliased fields |
| `omit_none` | Unset | Omit fields whose value is `None` |
| `omit_default` | Unset | Omit fields equal to defaults |
| `namedtuple_as_dict` | Unset | Represent named tuples as mappings |
| `allow_postponed_evaluation` | `True` | Defer compilation when a type reference is unresolved |
| `dialect` | `None` | Fixed default serialization dialect |
| `orjson_options` | `0` | Default orjson option bitmask |
| `json_schema` | `{}` | Dataclass-level JSON Schema overrides |
| `discriminator` | `None` | Polymorphic subtype selection |
| `lazy_compilation` | `False` | Compile generated methods on first use |
| `sort_keys` | `False` | Sort serialized dictionary keys |
| `forbid_extra_keys` | `False` | Reject unexpected input keys |

“Unset” is an internal sentinel rather than `False`, allowing a format dialect to provide a default while an explicit model value can override it.

## `debug`

Set `debug = True` to print the generated packing and unpacking source. This is useful when investigating configuration precedence, a performance issue, or an unexpected conversion.

```python
class Config(BaseConfig):
    debug = True
```

Generated source is an implementation detail. Use it for diagnosis, not as an API to copy or patch.

## `code_generation_options`

Optional features change generated method signatures and are therefore opt-in:

```python
from mashumaro.config import (
    ADD_DIALECT_SUPPORT,
    ADD_SERIALIZATION_CONTEXT,
    TO_DICT_ADD_BY_ALIAS_FLAG,
    TO_DICT_ADD_OMIT_NONE_FLAG,
)


class Config(BaseConfig):
    code_generation_options = [
        TO_DICT_ADD_BY_ALIAS_FLAG,
        TO_DICT_ADD_OMIT_NONE_FLAG,
        ADD_DIALECT_SUPPORT,
        ADD_SERIALIZATION_CONTEXT,
    ]
```

See [Code Generation Options](#/docs/code-generation-options) for the exact method parameters and propagation rules.

## `serialization_strategy`

Map target types to `SerializationStrategy` instances or dictionaries containing `serialize`/`deserialize` callables:

```python
from datetime import date


class Config(BaseConfig):
    serialization_strategy = {
        date: {
            "serialize": date.toordinal,
            "deserialize": date.fromordinal,
        }
    }
```

See [SerializationStrategy](#/docs/serializationstrategy) for subclass and generic matching.

## Aliases

### `aliases`

Define external names centrally:

```python
class Config(BaseConfig):
    aliases = {
        "user_id": "userId",
        "created_at": ["createdAt", "created_at", "CreatedAt"],
    }
```

Each value may be a string or an ordered sequence of strings. During deserialization, aliases are tried in order and the first key present in the input wins. The first alias is the primary name used for alias serialization and generated JSON Schema. An empty sequence uses the Python field name.

A per-field metadata alias overrides an `Annotated` alias, which overrides this mapping. Alias sources are not combined.

### `serialize_by_alias`

Aliases are input names by default. Set `serialize_by_alias = True` to use them for output too:

```python
from dataclasses import dataclass


@dataclass
class User(APIModel):
    user_id: int

    class Config(APIModel.Config):
        aliases = {"user_id": "userId"}
        serialize_by_alias = True


assert User(42).to_dict() == {"userId": 42}
```

### `allow_deserialization_not_by_alias`

With the default `False`, an aliased field accepts its alias and rejects its Python name. Set this option to accept both:

```python
class Config(BaseConfig):
    aliases = {"user_id": "userId"}
    allow_deserialization_not_by_alias = True
```

This is valuable for gradual API migrations. With multiple aliases, the Python field name is tried after every declared alias. If several accepted keys are present, the first declared alias wins.

## Omission rules

### `omit_none`

```python
from dataclasses import dataclass

from mashumaro import DataClassDictMixin


@dataclass
class Sparse(DataClassDictMixin):
    name: str
    description: str | None = None

    class Config(BaseConfig):
        omit_none = True


assert Sparse("item").to_dict() == {"name": "item"}
```

Only a current value of `None` is omitted. Empty strings, zero, `False`, and empty collections remain.

### `omit_default`

This option omits a field when its current value equals the declared default or the value produced by its default factory:

```python
from dataclasses import dataclass, field


@dataclass
class Preferences(DataClassDictMixin):
    theme: str = "system"
    tags: list[str] = field(default_factory=list)

    class Config(BaseConfig):
        omit_default = True


assert Preferences().to_dict() == {}
assert Preferences(theme="dark").to_dict() == {"theme": "dark"}
```

Default factories are evaluated to determine the comparison value. Keep them cheap and deterministic.

## `namedtuple_as_dict`

Set this option to represent every named tuple field as a mapping instead of the default list. A field-level `as_list` or `as_dict` engine can override the model-wide choice.

```python
class Config(BaseConfig):
    namedtuple_as_dict = True
```

Dictionary representation is more self-describing and tolerates omitted defaulted items; list representation is more compact.

## Forward references

### `allow_postponed_evaluation`

The default `True` lets Mashumaro postpone generated-method compilation when a referenced type is not defined yet. This supports string annotations, [`from __future__ import annotations`](https://docs.python.org/3/library/__future__.html#future-annotations), mutually recursive models, and Python 3.14's deferred annotation behavior.

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Node(DataClassDictMixin):
    value: int
    next: Node | None = None
```

With `allow_postponed_evaluation = False`, an unresolved type raises `UnresolvedTypeReferenceError` during class processing instead of deferring. Disable it when eager failure is more valuable than declaration-order flexibility.

## `dialect`

Set a fixed default dialect for this model:

```python
class Config(BaseConfig):
    dialect = PublicAPIDialect
```

A dialect class is required, not an instance. See [Dialects](#/docs/dialects) for call-time switching and codec defaults.

## `orjson_options`

Store the integer bitmask forwarded to [`orjson.dumps`](https://github.com/ijl/orjson#serialize) by `DataClassORJSONMixin.to_jsonb()`:

```python
import orjson


class Config(BaseConfig):
    orjson_options = orjson.OPT_SORT_KEYS | orjson.OPT_UTC_Z
```

The call-time `to_jsonb(orjson_options=...)` argument overrides this value for one call.

## `json_schema`

Dataclass-level schema overrides currently support the JSON Schema [`properties`](https://json-schema.org/understanding-json-schema/reference/object#properties) and [`additionalProperties`](https://json-schema.org/understanding-json-schema/reference/object#additional-properties) keywords:

```python
from mashumaro.jsonschema.models import JSONSchema


class Config(BaseConfig):
    json_schema = {
        "properties": {
            "name": {
                "type": "string",
                "description": "Public display name",
            }
        },
        "additionalProperties": JSONSchema(type=None),
    }
```

For field-level keywords, prefer `Annotated[..., JSONSchema(...)]`. See [JSON Schema](#/docs/json-schema).

## `discriminator`

Configure polymorphic deserialization for a model hierarchy:

```python
from mashumaro.types import Discriminator


class Config(BaseConfig):
    discriminator = Discriminator(
        field="type",
        include_subtypes=True,
    )
```

At least one of `include_subtypes` or `include_supertypes` must be enabled. See [Discriminator](#/docs/discriminator).

## Compilation controls

### `lazy_compilation`

With the default `False`, mixin methods are normally generated during class creation. Set `True` to defer work until the first serialization/deserialization call:

```python
class Config(BaseConfig):
    lazy_compilation = True
```

This can reduce import time in applications that define many models but use only a subset. The first call pays the compilation cost; subsequent calls use the generated method.

### `sort_keys`

Sort keys in each generated dictionary:

```python
class Config(BaseConfig):
    sort_keys = True
```

This makes basic output deterministic and propagates to nested dataclasses according to their own config. JSON encoders may also have a separate sort option; basic sorting happens before the format encoder.

## Strict input with `forbid_extra_keys`

The default ignores input keys that do not correspond to fields. Set strict mode to raise `ExtraKeysError`:

```python
from dataclasses import dataclass

from mashumaro.exceptions import ExtraKeysError


@dataclass
class Command(DataClassDictMixin):
    action: str

    class Config(BaseConfig):
        forbid_extra_keys = True


try:
    Command.from_dict({"action": "deploy", "force": True})
except ExtraKeysError as exc:
    assert exc.extra_keys == {"force"}
    assert exc.target_type is Command
```

All alias names count as expected keys. When `allow_deserialization_not_by_alias=True`, the Python field name is accepted too.

## Inheritance pattern

Configuration follows normal Python inheritance. Derive from the parent config when overriding options so inherited policy remains obvious:

```python
class PublicModel(DataClassDictMixin):
    class Config(BaseConfig):
        forbid_extra_keys = True
        omit_none = True


class InternalModel(PublicModel):
    class Config(PublicModel.Config):
        forbid_extra_keys = False
```

Use immutable-by-convention mappings and lists: do not mutate an inherited config collection at runtime, because class attributes can be shared.
