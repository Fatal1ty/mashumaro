---
title: API Reference
group: Reference
---

# API Reference

This is a compact map of the public entry points. Detailed behavior and examples live in the linked chapters.

## Top-level imports

```python
from mashumaro import (
    DataClassDictMixin,
    MissingField,
    field_options,
    pass_through,
)
```

`DataClassDictMixin` adds the basic-form methods. `field_options()` builds dataclass metadata. `pass_through` is the identity serialization strategy.

Format mixins intentionally live in their own modules:

```python
from mashumaro.mixins.json import DataClassJSONMixin
from mashumaro.mixins.msgpack import DataClassMessagePackMixin
from mashumaro.mixins.orjson import DataClassORJSONMixin
from mashumaro.mixins.toml import DataClassTOMLMixin
from mashumaro.mixins.yaml import DataClassYAMLMixin
```

## Mixin methods

### Basic form

```text
obj.to_dict(**generated_options) -> dict
Model.from_dict(mapping, **generated_options) -> Model
```

Possible generated options are `omit_none`, `by_alias`, `dialect`, and serialization-only `context`; each requires its [code generation flag](#/docs/code-generation-options).

### Standard JSON

The default callables are the standard-library [`json.dumps`](https://docs.python.org/3/library/json.html#json.dumps) and [`json.loads`](https://docs.python.org/3/library/json.html#json.loads).

```text
obj.to_json(encoder=json.dumps, **to_dict_kwargs) -> str | bytes | bytearray
Model.from_json(data, decoder=json.loads, **from_dict_kwargs) -> Model
```

### orjson

The [orjson API](https://github.com/ijl/orjson) defines the accepted options, native values, bytes return type, and errors.

```text
obj.to_jsonb(
    encoder=orjson.dumps,
    *,
    orjson_options=...,
    **to_dict_kwargs,
) -> bytes
obj.to_json(**kwargs) -> str
Model.from_json(data, decoder=orjson.loads, **from_dict_kwargs) -> Model
```

### YAML

Default loaders and dumpers come from [PyYAML](https://pyyaml.org/wiki/PyYAMLDocumentation).

```text
obj.to_yaml(encoder=default_encoder, **to_dict_kwargs) -> str | bytes
Model.from_yaml(data, decoder=default_decoder, **from_dict_kwargs) -> Model
```

### TOML

Reading uses [`tomllib`](https://docs.python.org/3/library/tomllib.html) where available and writing uses [`tomli-w`](https://pypi.org/project/tomli-w/).

```text
obj.to_toml(encoder=tomli_w.dumps, **to_dict_kwargs) -> str
Model.from_toml(data, decoder=tomllib.loads, **from_dict_kwargs) -> Model
```

### MessagePack

The defaults wrap the [`msgpack` API](https://msgpack-python.readthedocs.io/en/stable/api.html).

```text
obj.to_msgpack(encoder=default_encoder, **to_dict_kwargs) -> bytes
Model.from_msgpack(data, decoder=default_decoder, **from_dict_kwargs) -> Model
```

See [Supported Formats](#/docs/supported-formats) for dependencies and native representations.

## Reusable codecs

### Basic

```text
from mashumaro.codecs import BasicDecoder, BasicEncoder

BasicDecoder(
    shape_type,
    *,
    default_dialect=None,
    pre_decoder_func=None,
)
BasicEncoder(
    shape_type,
    *,
    default_dialect=None,
    post_encoder_func=None,
)
```

Instances expose `.decode(data)` and `.encode(obj)`.

### Standard JSON

```text
from mashumaro.codecs.json import JSONDecoder, JSONEncoder

JSONDecoder(
    shape_type,
    *,
    default_dialect=None,
    pre_decoder_func=json.loads,
)
JSONEncoder(
    shape_type,
    *,
    default_dialect=None,
    post_encoder_func=json.dumps,
)
```

### orjson

```text
from mashumaro.codecs.orjson import ORJSONDecoder, ORJSONEncoder

ORJSONDecoder(shape_type, *, default_dialect=None)
ORJSONEncoder(shape_type, *, default_dialect=None)
```

The encoder returns bytes. The built-in orjson parser/renderer is fixed in the codec.

### YAML

```text
from mashumaro.codecs.yaml import YAMLDecoder, YAMLEncoder

YAMLDecoder(shape_type, *, default_dialect=None, pre_decoder_func=...)
YAMLEncoder(shape_type, *, default_dialect=None, post_encoder_func=...)
```

### TOML

```text
from mashumaro.codecs.toml import TOMLDecoder, TOMLEncoder

TOMLDecoder(shape_type, *, default_dialect=None)
TOMLEncoder(shape_type, *, default_dialect=None)
```

### MessagePack

```text
from mashumaro.codecs.msgpack import (
    MessagePackDecoder,
    MessagePackEncoder,
)

MessagePackDecoder(
    shape_type, *, default_dialect=None, pre_decoder_func=...
)
MessagePackEncoder(
    shape_type, *, default_dialect=None, post_encoder_func=...
)
```

## One-off codec functions

| Module | Named functions | Short aliases |
|---|---|---|
| `mashumaro.codecs.basic` | `encode`, `decode` | Same |
| `mashumaro.codecs.json` | `json_encode`, `json_decode` | `encode`, `decode` |
| `mashumaro.codecs.orjson` | `json_encode`, `json_decode` | `encode`, `decode` |
| `mashumaro.codecs.yaml` | `yaml_encode`, `yaml_decode` | `encode`, `decode` |
| `mashumaro.codecs.toml` | `toml_encode`, `toml_decode` | `encode`, `decode` |
| `mashumaro.codecs.msgpack` | `msgpack_encode`, `msgpack_decode` | `encode`, `decode` |

Every encode function takes `(obj, shape_type)` and every decode function takes `(data, shape_type)`. Standard JSON additionally accepts its transform function as an optional third argument.

## Configuration

```python
from mashumaro.config import (
    ADD_DIALECT_SUPPORT,
    ADD_SERIALIZATION_CONTEXT,
    TO_DICT_ADD_BY_ALIAS_FLAG,
    TO_DICT_ADD_OMIT_NONE_FLAG,
    BaseConfig,
)
```

`BaseConfig` attributes:

- `debug`
- `code_generation_options`
- `serialization_strategy`
- `aliases`
- `serialize_by_alias`
- `namedtuple_as_dict`
- `allow_postponed_evaluation`
- `dialect`
- `omit_none`
- `omit_default`
- `orjson_options`
- `json_schema`
- `discriminator`
- `lazy_compilation`
- `sort_keys`
- `allow_deserialization_not_by_alias`
- `forbid_extra_keys`

See [Config Options](#/docs/config-options) for defaults and precedence.

## Dialect

```python
from mashumaro.dialect import Dialect
```

Subclass attributes are `serialization_strategy`, `serialize_by_alias`, `namedtuple_as_dict`, `omit_none`, `omit_default`, and `no_copy_collections`. `Dialect.merge(other)` returns a new dialect class; see [Dialects](#/docs/dialects#merging-dialects).

## Extension types

```python
from mashumaro.types import (
    Alias,
    Discriminator,
    GenericSerializableType,
    RoundedDecimal,
    SerializableType,
    SerializationStrategy,
)
```

### `SerializableType`

```python
class Custom(SerializableType, use_annotations=False):
    def _serialize(self): ...

    @classmethod
    def _deserialize(cls, value): ...
```

### `GenericSerializableType`

```python
def _serialize(self, types): ...

@classmethod
def _deserialize(cls, value, types): ...
```

### `SerializationStrategy`

```python
class Strategy(
    SerializationStrategy,
    use_annotations=False,
    match_subclasses=False,
):
    def serialize(self, value): ...
    def deserialize(self, value): ...
```

### `RoundedDecimal`

```text
RoundedDecimal(places: int | None = None, rounding: str | None = None)
```

### `Discriminator`

```text
Discriminator(
    field: str | None = None,
    include_supertypes: bool = False,
    include_subtypes: bool = False,
    variant_tagger_fn=None,
)
```

### `Alias`

```python
Annotated[int, Alias("externalName")]
```

[`Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated) preserves the underlying static type while carrying Mashumaro's runtime metadata.

## Field helper

```text
from mashumaro import field_options

field_options(
    serialize=None,
    deserialize=None,
    serialization_strategy=None,
    alias=None,
    **extra_metadata,
) -> dict
```

See [Field Options](#/docs/field-options).

## JSON Schema

The supported targets are [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/json-schema-core) and the [OpenAPI 3.1 Schema Object](https://spec.openapis.org/oas/v3.1.0.html#schema-object).

```python
from mashumaro.jsonschema import (
    DRAFT_2020_12,
    OPEN_API_3_1,
    JSONSchemaBuilder,
    build_json_schema,
)
```

```python
build_json_schema(
    instance_type,
    context=None,
    with_definitions=True,
    all_refs=None,
    with_dialect_uri=False,
    dialect=None,
    ref_prefix=None,
    plugins=(),
)
```

```python
JSONSchemaBuilder(
    dialect=DRAFT_2020_12,
    all_refs=None,
    ref_prefix=None,
    plugins=(),
)
```

The builder exposes `.build(instance_type)` and `.get_definitions()`.

## Exceptions

Import exceptions from `mashumaro.exceptions`. Their attributes and recommended handling are documented in [Errors and Troubleshooting](#/docs/errors-and-troubleshooting#exception-reference).

## Stable versus internal modules

Build integrations from the public modules shown here. Names under `mashumaro.core` and generated private methods are implementation details and may change without serving as a user-facing extension contract.
