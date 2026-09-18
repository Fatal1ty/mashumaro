---
title: JSON Schema
group: Advanced
---

# JSON Schema

Mashumaro builds [JSON Schema](https://json-schema.org/specification) for any [supported type shape](#/docs/supported-types), not only dataclasses. The result is a typed `JSONSchema` object with `to_dict()` and `to_json()` methods.

Built-in schema dialects cover [**JSON Schema Draft 2020-12**](https://json-schema.org/draft/2020-12/json-schema-core) and [**OpenAPI 3.1**](https://spec.openapis.org/oas/v3.1.0.html#schema-object).

## Build a schema

```python
from dataclasses import dataclass, field
from uuid import UUID

from mashumaro.jsonschema import build_json_schema


@dataclass
class User:
    id: UUID
    name: str = field(metadata={"description": "Public display name"})
    email: str | None = None


schema = build_json_schema(User)
schema_dict = schema.to_dict()
schema_json = schema.to_json()
```

The essential output is equivalent to:

```json
{
  "type": "object",
  "title": "User",
  "properties": {
    "id": {"type": "string", "format": "uuid"},
    "name": {"type": "string", "description": "Public display name"},
    "email": {
      "anyOf": [{"type": "string"}, {"type": "null"}],
      "default": null
    }
  },
  "additionalProperties": false,
  "required": ["id", "name"]
}
```

Dataclass fields without defaults are required. Defaults are serialized into the schema using the model's serialization rules. Aliases become property names. When a field has multiple aliases, JSON Schema uses the first (primary) alias, including aliases declared by repeating `Alias(...)` in `Annotated`:

```python
from typing import Annotated

from mashumaro.types import Alias


@dataclass
class LegacyUser:
    user_id: Annotated[int, Alias("userId"), Alias("UserID")]


schema = build_json_schema(LegacyUser)
assert set(schema.properties) == {"userId"}
assert schema.required == ["userId"]
```

## Non-dataclass root shapes

```python
from mashumaro.jsonschema import build_json_schema

users_schema = build_json_schema(list[User])
lookup_schema = build_json_schema(dict[str, User | None])
tuple_schema = build_json_schema(tuple[int, str, bool])
```

Codecs and schema generation therefore share the same “shape type” vocabulary.

## `build_json_schema` options

| Argument | Default | Purpose |
|---|---|---|
| `instance_type` | Required | Dataclass or any supported shape |
| `context` | New context | Reuse definitions and plugin state |
| `with_definitions` | `True` | Attach accumulated definitions to the result |
| `all_refs` | Dialect default | Put all dataclasses in definitions and reference them |
| `with_dialect_uri` | `False` | Emit the `$schema` keyword |
| `dialect` | Draft 2020-12 | Select schema dialect |
| `ref_prefix` | Dialect default | Override the reference root |
| `plugins` | Empty | Extend or modify generated schemas |

## Schema dialects

Draft 2020-12 is the default:

```python
from mashumaro.jsonschema import DRAFT_2020_12, build_json_schema

schema = build_json_schema(
    User,
    dialect=DRAFT_2020_12,
    with_dialect_uri=True,
)
assert schema.to_dict()["$schema"] == (
    "https://json-schema.org/draft/2020-12/schema"
)
```

OpenAPI 3.1 uses `#/components/schemas` references and references dataclasses by default:

```python
from mashumaro.jsonschema import OPEN_API_3_1, build_json_schema

schema = build_json_schema(
    list[User],
    dialect=OPEN_API_3_1,
    with_dialect_uri=True,
)
```

| Dialect | Definition pointer | Default `all_refs` |
|---|---|---|
| `DRAFT_2020_12` | `#/$defs` | `False` |
| `OPEN_API_3_1` | `#/components/schemas` | `True` |

## References and definitions

Set `all_refs=True` to replace every dataclass occurrence with a reference and collect definitions:

```python
schema = build_json_schema(list[User], all_refs=True)

document = schema.to_dict()
assert document["items"]["$ref"].endswith("/User")
assert "User" in document["$defs"]
```

Set `with_definitions=False` when embedding the returned fragment in a larger document that stores definitions elsewhere:

```python
fragment = build_json_schema(
    list[User],
    dialect=OPEN_API_3_1,
    with_definitions=False,
)
```

Override the reference root when the destination uses another component location:

```python
fragment = build_json_schema(
    list[User],
    all_refs=True,
    with_definitions=False,
    ref_prefix="#/components/responses",
)
```

Trailing slashes are normalized. Recursive dataclasses and recursive type aliases force definitions/references as needed even when `all_refs=False`, preventing infinite inline expansion.

## Incremental `JSONSchemaBuilder`

Use a builder when assembling a larger OpenAPI or schema document from many models:

```python
from dataclasses import dataclass
from uuid import UUID

from mashumaro.jsonschema import JSONSchemaBuilder, OPEN_API_3_1


@dataclass
class Device:
    id: UUID
    model: str


builder = JSONSchemaBuilder(dialect=OPEN_API_3_1)

users_fragment = builder.build(list[User]).to_dict()
devices_fragment = builder.build(list[Device]).to_dict()
definitions = builder.get_definitions().to_dict()

assert "User" in definitions
assert "Device" in definitions
```

The builder shares one `Context`, so definitions accumulate across calls. Constructor options are `dialect`, `all_refs`, `ref_prefix`, and `plugins`.

## Type-to-schema mapping

| Python shape | Schema shape |
|---|---|
| `str` | `{"type": "string"}` |
| `int` | `{"type": "integer"}` |
| `float` | `{"type": "number"}` |
| `Decimal`, `Fraction` | String with Mashumaro's `decimal`/`fraction` format extension |
| `bool` | `{"type": "boolean"}` |
| `None` | `{"type": "null"}` |
| `Any` | Empty unrestricted schema |
| `Literal[...]`, `Enum` | `enum` values |
| `A | B` | `anyOf` |
| `list[T]`, sequences | Array with `items` |
| Fixed `tuple[...]` | Array with `prefixItems`, `minItems`, `maxItems` |
| `set[T]`, `frozenset[T]` | Array with `uniqueItems` |
| Mapping | Object with `propertyNames`/`additionalProperties` |
| `TypedDict` | Object properties, required keys, and extra-item policy |
| Dataclass | Closed object with properties and required keys |
| `datetime`, `date`, `time` | String with standard format |
| `UUID`, IP addresses | String with standard format |
| `slice` | Array of three `integer` or `null` items (`[start, stop, step]`) |
| `bytes` | String with Mashumaro's `base64` format extension |
| Paths | String with Mashumaro's `path` format extension |

Mashumaro also defines extension formats for time zones, timedelta, networks, IP interfaces, decimal, fraction, and Base64 where the standard [JSON Schema format vocabulary](https://json-schema.org/draft/2020-12/json-schema-validation#name-defined-formats) has no exact built-in format.

## TypedDict extra items

[PEP 728](https://peps.python.org/pep-0728/) controls whether a `TypedDict` accepts keys that are not declared in its class body. Mashumaro maps its options to JSON Schema's `additionalProperties` keyword:

| `TypedDict` declaration | Generated `additionalProperties` |
|---|---|
| `closed=True` | `false` |
| `closed=False` | `true` |
| `extra_items=T` | The generated schema for `T` |

Use either `closed` or `extra_items`, not both. Starting with Python 3.15, these options are available on `typing.TypedDict` out of the box. On earlier Python versions, import `TypedDict` from `typing_extensions` instead. The example below uses the backport for compatibility with older Python versions:

```python
from typing_extensions import TypedDict

from mashumaro.jsonschema import build_json_schema


class ClosedPayload(TypedDict, closed=True):
    name: str


class OpenPayload(TypedDict, closed=False):
    name: str


class StringExtrasPayload(TypedDict, extra_items=str):
    name: str


assert build_json_schema(ClosedPayload).additionalProperties is False
assert build_json_schema(OpenPayload).additionalProperties is True
assert build_json_schema(StringExtrasPayload).to_dict()[
    "additionalProperties"
] == {"type": "string"}
```

There is one compatibility exception when neither option is specified:

> [!IMPORTANT]
> For a `TypedDict` that specifies neither option, current Mashumaro releases generate `additionalProperties: false`. This deliberately preserves the schema produced by earlier releases, although PEP 728 defines an ordinary `TypedDict` as open, equivalent to `closed=False`. A future major Mashumaro release will change this default to `additionalProperties: true`. If a schema is intended to remain closed, declare `closed=True` explicitly now; use `closed=False` to opt into the PEP default today.

## Constraints with `Annotated`

Constraint objects in `mashumaro.jsonschema.annotations` add [Draft 2020-12 validation keywords](https://json-schema.org/draft/2020-12/json-schema-validation) while preserving the runtime type with [`Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated):

```python
from dataclasses import dataclass
from typing import Annotated

from mashumaro.jsonschema.annotations import (
    MaxItems,
    MaxLength,
    Maximum,
    MinItems,
    MinLength,
    Minimum,
    Pattern,
    UniqueItems,
)


@dataclass
class Product:
    sku: Annotated[str, Pattern(r"^[A-Z]{2}\d{6}$")]
    name: Annotated[str, MinLength(1), MaxLength(100)]
    price: Annotated[float, Minimum(0), Maximum(1_000_000)]
    tags: Annotated[
        list[str], MinItems(1), MaxItems(20), UniqueItems(True)
    ]
```

### Numeric constraints

- `Minimum(value)`
- `Maximum(value)`
- `ExclusiveMinimum(value)`
- `ExclusiveMaximum(value)`
- `MultipleOf(value)`

### String constraints

- `MinLength(value)`
- `MaxLength(value)`
- `Pattern(value)`

### Array constraints

- `MinItems(value)`
- `MaxItems(value)`
- `UniqueItems(value)`
- `Contains(JSONSchema(...))`
- `MinContains(value)`
- `MaxContains(value)`

`MinContains` and `MaxContains` are emitted only when `Contains` is present, matching the [JSON Schema array-keyword semantics](https://json-schema.org/understanding-json-schema/reference/array#contains).

### Object constraints

- `MinProperties(value)`
- `MaxProperties(value)`
- `DependentRequired(mapping)`

Apply collection constraints to the collection's `Annotated` layer and element constraints to the element layer:

```python
from mashumaro.jsonschema.annotations import MaxItems, Maximum

Scores = Annotated[
    list[Annotated[int, Maximum(100)]],
    MaxItems(10),
]
```

## Schema overlays with `JSONSchema`

Attach a `JSONSchema` instance inside `Annotated` for keywords that do not have a dedicated constraint class:

```python
from dataclasses import dataclass
from typing import Annotated

from mashumaro.jsonschema.models import JSONSchema, JSONSchemaInstanceType


@dataclass
class Upload:
    file: Annotated[
        bytes,
        JSONSchema(
            description="PDF document",
            contentEncoding="base64",
            contentMediaType="application/pdf",
        ),
    ]
    metadata: Annotated[
        str,
        JSONSchema(
            contentMediaType="application/json",
            contentSchema=JSONSchema(
                type=JSONSchemaInstanceType.OBJECT
            ),
        ),
    ]
```

Overlay values are applied after automatic type generation and combine with constraint annotations. If multiple overlays set the same attribute, the last one wins. Explicit `None` for `const` and `default` is preserved.

> [!NOTE]
> Structural keywords [`$schema`](https://json-schema.org/understanding-json-schema/reference/schema#schema), [`$ref`](https://json-schema.org/understanding-json-schema/structuring#dollarref), and [`$defs`](https://json-schema.org/understanding-json-schema/structuring#defs) are ignored in field overlays; they are controlled by builder context and reference options.

## Field metadata and model overrides

A field's [`metadata={"description": ...}`](https://docs.python.org/3/library/dataclasses.html#dataclasses.field) supplies its description:

```python
name: str = field(metadata={"description": "Public display name"})
```

For dataclass-level overrides, `Config.json_schema` supports property replacements and `additionalProperties`:

```python
from mashumaro.config import BaseConfig


@dataclass
class Flexible:
    name: str

    class Config(BaseConfig):
        json_schema = {
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Overridden field schema",
                }
            },
            "additionalProperties": True,
        }
```

An `additionalProperties` override may be `True`, `False`, or a `JSONSchema` object. A property override replaces that field's automatically generated schema; an `Annotated` overlay modifies the generated schema. Prefer overlays for additive field customization.

## Custom serialization and schema output

Schema describes the serialized representation, not only the Python annotation. Give custom serializers return annotations so Mashumaro can follow the output type:

```python
from dataclasses import dataclass, field

from mashumaro.config import BaseConfig


def string_as_characters(value: str) -> list[str]:
    return list(value)


def integer_as_string(value: int) -> str:
    return str(value)


@dataclass
class CustomWireShape:
    name: str = field(metadata={"serialize": string_as_characters})
    count: int = 0

    class Config(BaseConfig):
        serialization_strategy = {
            int: {"serialize": integer_as_string}
        }
```

The schema for `name` becomes an array of strings and `count` becomes a string. If a callable lacks a return annotation or the annotation cannot be resolved, the builder warns and falls back to an unrestricted schema.

The same principle applies to annotation-aware `SerializableType` and `SerializationStrategy` methods.

## Plugins

Plugins can add an unsupported type or modify an existing schema. They run in order for every instance in the shape.

The built-in docstring plugin adds Python [class docstrings](https://docs.python.org/3/tutorial/controlflow.html#documentation-strings) from dataclasses:

```python
from mashumaro.jsonschema import build_json_schema
from mashumaro.jsonschema.plugins import DocstringDescriptionPlugin


@dataclass
class Region:
    """A deployment region."""

    name: str


schema = build_json_schema(
    Region, plugins=[DocstringDescriptionPlugin()]
)
assert schema.description == "A deployment region."
```

### Custom plugin

```python
from pathlib import Path

from mashumaro.jsonschema.models import (
    Context,
    JSONSchema,
    JSONSchemaInstanceType,
)
from mashumaro.jsonschema.plugins import BasePlugin
from mashumaro.jsonschema.schema import Instance


class PathDescriptionPlugin(BasePlugin):
    def get_schema(
        self,
        instance: Instance,
        ctx: Context,
        schema: JSONSchema | None = None,
    ) -> JSONSchema | None:
        try:
            if issubclass(instance.type, Path) and schema is not None:
                schema.type = JSONSchemaInstanceType.STRING
                schema.description = "Filesystem path"
                return schema
        except TypeError:
            return None
        return None
```

Returning a schema replaces/continues the current result. Returning `None` or raising `NotImplementedError` means the plugin does not handle that instance. A plugin may receive `schema=None` for a type unsupported by built-in creators and can return a complete schema to add support.

Register the same plugin list on `build_json_schema(..., plugins=[...])` or `JSONSchemaBuilder(plugins=[...])`.

## Recursive models and aliases

Direct recursion, mutual recursion, [`typing.Self`](https://docs.python.org/3/library/typing.html#typing.Self), and [PEP 695](https://peps.python.org/pep-0695/) recursive aliases are supported. The builder creates definitions automatically when it encounters a cycle:

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Node:
    value: int
    children: list[Node]


schema = build_json_schema(Node)
assert "$defs" in schema.to_dict()
```

## Practical checklist

- Build schemas from the same concrete shape passed to your codec.
- Use aliases consistently so schema property names match actual output.
- Annotate custom serializer return types.
- Choose Draft 2020-12 or OpenAPI 3.1 before deciding reference layout.
- Use `JSONSchemaBuilder` when assembling multiple components.
- Prefer `Annotated` constraints and overlays for field-local additions.
- Snapshot or structurally test generated schemas as part of API compatibility checks.
- Remember that JSON Schema documents the serialized contract; it does not execute Mashumaro deserialization.
