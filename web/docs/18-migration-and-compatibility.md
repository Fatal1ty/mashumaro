---
title: Migration and Compatibility
group: Reference
---

# Migration and Compatibility

Mashumaro follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html). Review the [GitHub Releases](https://github.com/Fatal1ty/mashumaro/releases) notes before upgrading across a major version and keep exact wire-contract tests for serialized data that outlives a deployment.

## Supported Python versions

The current {{PACKAGE_VERSION}} release supports Python {{PYTHON_VERSION_RANGE}}.

| Retired Python | Last compatible mashumaro |
|---|---|
| 3.9 | 3.20 |
| 3.8 | 3.14 |
| 3.7 | 3.9.1 |
| 3.6 | 3.1.1 |

If an application must stay on an [end-of-life interpreter](https://devguide.python.org/versions/), pin both the library and optional format dependencies. The preferred migration is to upgrade Python and then use the current Mashumaro release.

## Migrating from version 2 to 3

### Format mixin imports moved

Use format-specific modules:

```python
from mashumaro.mixins.json import DataClassJSONMixin
from mashumaro.mixins.msgpack import DataClassMessagePackMixin
from mashumaro.mixins.yaml import DataClassYAMLMixin
```

`DataClassDictMixin` remains available from `mashumaro`.

### `use_bytes` was removed

Replace pass-through behavior with a dialect:

```python
from mashumaro import pass_through
from mashumaro.dialect import Dialect


class BytesDialect(Dialect):
    serialization_strategy = {
        bytes: pass_through,
        bytearray: pass_through,
    }
```

Enable `ADD_DIALECT_SUPPORT` for call-time use or set `Config.dialect`. Ensure the final encoder supports raw binary; standard JSON does not.

### `use_enum` was removed

Use a strategy/dialect with `pass_through` when the downstream format accepts enum objects, or define an explicit by-name/by-value strategy. Default Mashumaro behavior serializes [`Enum.value`](https://docs.python.org/3/library/enum.html#enum.Enum.value).

### `use_datetime` was removed

Use a dialect that passes `datetime`, `date`, and `time` through. [TOML](https://toml.io/en/v1.0.0) and [orjson](https://github.com/ijl/orjson) already ship format dialects with appropriate native handling. For JSON, prefer an explicit textual or numeric strategy because [`json.dumps`](https://docs.python.org/3/library/json.html#json.dumps) does not accept datetime objects by default.

### Format method signatures changed

Version 2 accepted `dict_params` and arbitrary final encoder/decoder keyword arguments. Version 3 forwards extra method keywords to the generated dictionary conversion layer:

```python
Model.from_json(data, decoder=custom_decoder, **from_dict_kwargs)
model.to_json(encoder=custom_encoder, **to_dict_kwargs)
```

Bind format-library options with a lambda or [`functools.partial`](https://docs.python.org/3/library/functools.html#functools.partial):

```python
import json
from decimal import Decimal
from functools import partial

loads_decimal = partial(json.loads, parse_float=Decimal)
dumps_unicode = partial(json.dumps, ensure_ascii=False)

model = Model.from_json(data, decoder=loads_decimal)
text = model.to_json(encoder=dumps_unicode)
```

## Evolving a wire model safely

### Add a field

Give a new field a [dataclass default or default factory](https://docs.python.org/3/library/dataclasses.html#default-factory-functions) so old payloads remain readable:

```python
@dataclass
class User(DataClassDictMixin):
    name: str
    tags: list[str] = field(default_factory=list)
```

Whether old readers tolerate the new output depends on their unknown-key policy. Coordinate `forbid_extra_keys` rollouts.

### Rename a field

Keep one stable output alias while accepting historical names and the Python field name during migration:

```python
class Config(BaseConfig):
    aliases = {
        "display_name": ["displayName", "name", "display_name_v1"]
    }
    serialize_by_alias = True
    allow_deserialization_not_by_alias = True
```

The first alias, `displayName`, is the canonical output name. The remaining aliases are accepted in order during deserialization, and `display_name` is accepted as the final fallback because `allow_deserialization_not_by_alias` is enabled.

### Change a field representation

A date string changed to epoch seconds is a breaking wire change even if the Python field remains `datetime`. Introduce a protocol version or a new dialect, read both representations during a defined transition, and emit only the new canonical representation.

### Add a polymorphic variant

Tagged discriminators make this additive for new readers, but old readers still reject unknown tags unless they have a supertype fallback. Decide explicitly whether unknown variants should fail, be stored raw, or map to a base model.

### Tighten unknown-key handling

Enabling `forbid_extra_keys` is behaviorally breaking for payloads that previously contained ignored fields. Audit real traffic or stored fixtures first.

## Compatibility test suite

Keep fixtures for every supported protocol/storage version and test:

- Old payload → current model.
- Current model → exact current payload.
- Missing newly optional fields.
- Legacy aliases and canonical output.
- Unknown fields and discriminator tags.
- Boundary dates, decimals, bytes, and enum values.
- Generated [JSON Schema](https://json-schema.org/specification) snapshots.
- Python {{MIN_PYTHON_VERSION}} and {{MAX_PYTHON_VERSION}} at minimum when modern annotations are used.

Exact output assertions catch symmetrical representation changes that a simple `decode(encode(x)) == x` round trip will miss.

## Upgrade checklist

- Read release notes and Python requirement changes.
- Install all optional format extras in a clean environment.
- Run tests with eager compilation so schema errors fail early.
- Run the oldest/newest supported Python jobs.
- Rebuild JSON Schema and compare contract snapshots.
- Exercise stored production fixtures and unknown-key policy.
- Benchmark hot codecs after, not before, semantic compatibility is confirmed.
