---
title: Errors and Troubleshooting
group: Guides
---

# Errors and Troubleshooting

Mashumaro raises specific exceptions for schema construction, input conversion, hooks, dialects, and optional integrations. Catch narrow exceptions at external boundaries and keep programming/configuration errors visible during development.

## Exception reference

| Exception | Typical stage | Meaning |
|---|---|---|
| `MissingField` | Deserialization | Required field key is absent |
| `ExtraKeysError` | Deserialization | Unexpected keys with `forbid_extra_keys=True` |
| `InvalidFieldValue` | Deserialization | A field value could not be converted |
| `UnserializableDataError` | Code generation | Base error for unsupported data shapes |
| `UnserializableField` | Code generation | A particular dataclass field is unsupported |
| `UnsupportedSerializationEngine` | Code generation | Unknown/inapplicable `serialize` engine |
| `UnsupportedDeserializationEngine` | Code generation | Unknown/inapplicable `deserialize` engine |
| `MissingDiscriminatorError` | Deserialization | Configured discriminator key is absent |
| `SuitableVariantNotFoundError` | Deserialization | No discriminator variant matched |
| `BadHookSignature` | Class processing | Hook kind or parameters are invalid |
| `ThirdPartyModuleNotFoundError` | Class processing/use | Requested parser integration is not installed |
| `UnresolvedTypeReferenceError` | Class processing | A forward reference cannot be resolved |
| `BadDialect` | Code generation/call | Dialect is invalid or passed in the wrong form |

All live in `mashumaro.exceptions`.

## Missing required fields

```python
from dataclasses import dataclass

from mashumaro import DataClassDictMixin
from mashumaro.exceptions import MissingField


@dataclass
class User(DataClassDictMixin):
    name: str
    age: int = 0


try:
    User.from_dict({"age": 30})
except MissingField as exc:
    assert exc.field_name == "name"
    assert exc.field_type is str
    assert exc.holder_class is User
```

A dataclass [`default` or `default_factory`](https://docs.python.org/3/library/dataclasses.html#default-factory-functions) makes missing input legal. [`Optional[T]`](https://docs.python.org/3/library/typing.html#typing.Optional) does not automatically make a field optional in the mapping; it only allows `None`. Give it a default when omission is valid:

```python
nickname: str | None = None
```

For an alias, the alias is the required input key unless `allow_deserialization_not_by_alias=True`.

## Unexpected keys

```python
from dataclasses import dataclass

from mashumaro.config import BaseConfig
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

Strict mode is best at public boundaries. During a rolling migration, normalize legacy keys in `__pre_deserialize__` before strict checking or explicitly allow both an alias and the Python name.

## Invalid values

`InvalidFieldValue` wraps a failure to construct the annotated type:

```python
from dataclasses import dataclass

from mashumaro.exceptions import InvalidFieldValue


@dataclass
class Item(DataClassDictMixin):
    count: int


try:
    Item.from_dict({"count": "many"})
except InvalidFieldValue as exc:
    assert exc.field_name == "count"
    assert exc.field_type is int
    assert exc.field_value == "many"
    assert exc.holder_class is Item
```

Inspect `exc.msg` and the [chained exception](https://docs.python.org/3/tutorial/errors.html#exception-chaining) when available. The most common causes are a wrong wire representation, a serializer/deserializer pair that disagrees, an invalid literal/enum value, or an ambiguous union.

Do not catch every `ValueError` around a full payload. Catch `InvalidFieldValue` and report the structured field context.

## Unsupported fields and engines

An arbitrary class is not serialized from `__dict__` automatically. This example uses the standard library's [`queue.Queue`](https://docs.python.org/3/library/queue.html#queue.Queue):

```python
from queue import Queue


@dataclass
class Unsupported(DataClassDictMixin):
    queue: Queue
```

Depending on compilation mode, defining or first using this class raises `UnserializableField`. Add an explicit `SerializableType`, strategy, field callable, or pass-through rule appropriate to the final format.

Engine names are type-specific. `as_dict`/`as_list` apply to named tuples; `ciso8601`/`pendulum` apply to date/time types; `omit` is serialization-only. A typo or incompatible engine raises `UnsupportedSerializationEngine` or `UnsupportedDeserializationEngine`.

## Missing optional parser modules

Selecting `deserialize="ciso8601"` or `deserialize="pendulum"` does not install [`ciso8601`](https://pypi.org/project/ciso8601/) or [`pendulum`](https://pendulum.eustace.io/docs/#parsing). Missing modules raise `ThirdPartyModuleNotFoundError` with:

- `module_name`
- `field_name`
- `holder_class`

Install the dependency explicitly and include it in your application's [requirements or lock file](https://packaging.python.org/en/latest/tutorials/managing-dependencies/).

Format mixins have their own extras; see [Supported Formats](#/docs/supported-formats).

## Forward-reference failures

`UnresolvedTypeReferenceError` identifies the holder class and unresolved name:

```python
class Config(BaseConfig):
    allow_postponed_evaluation = False
```

Common fixes:

- Keep `allow_postponed_evaluation=True`, the default.
- Add [`from __future__ import annotations`](https://docs.python.org/3/library/__future__.html#future-annotations) on Python 3.10–3.13.
- Import the referenced type before the model is first used.
- Avoid references hidden only under [`TYPE_CHECKING`](https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKING) when runtime evaluation needs them.
- For local-scope models, ensure the referenced object remains resolvable in the expected namespace.

Use `Config.debug=True` to see when compilation happens and what concrete type was resolved.

## Discriminator failures

`MissingDiscriminatorError.field_name` identifies an absent tag key. `SuitableVariantNotFoundError` exposes:

- `variants_type`
- `discriminator_name`
- `discriminator_value`

If a valid subclass is ignored, check that the tag attribute is defined directly on that concrete descendant, not only inherited. If a custom `variant_tagger_fn` is used, verify that it returns stable unique values and that the input tag has the same basic type.

For untagged variants, enable `forbid_extra_keys` where suitable and make required fields sufficiently distinct; otherwise a broader class may succeed before the intended one.

## Hook failures

The two deserialization hooks must be classmethods:

```python
@classmethod
def __pre_deserialize__(cls, data): ...

@classmethod
def __post_deserialize__(cls, obj): ...
```

Serialization hooks are instance methods. Context parameters are legal only with `ADD_SERIALIZATION_CONTEXT`. A wrong signature raises `BadHookSignature` during code generation.

Every hook must return the transformed value. Forgetting `return data`, `return obj`, or `return self` often produces a later error that looks unrelated.

## Dialect failures

Pass a dialect class:

```python
model.to_dict(dialect=PublicAPIDialect)
```

Do not pass `PublicAPIDialect()`. Also enable `ADD_DIALECT_SUPPORT` before using the call-time keyword. A fixed `Config.dialect` does not require the flag.

If a merged dialect appears to lose alias or named-tuple behavior, remember that `Dialect.merge()` currently merges strategies, omission flags, and `no_copy_collections`; define `serialize_by_alias` and `namedtuple_as_dict` explicitly on the final class.

## “Object is not JSON serializable”

This message usually comes from [`json.dumps`](https://docs.python.org/3/library/json.html#json.dumps), after Mashumaro's typed stage. Typical causes:

- `pass_through` left a custom object in the basic form.
- A custom serializer returned a non-JSON value.
- A dictionary has unsupported key types.
- A codec transform returned the wrong layer.
- A format-native dialect was reused with a different encoder.

Inspect `obj.to_dict()` or a `BasicEncoder` result first. If the unsupported object is already present there, fix the strategy. If the basic form is JSON-safe, inspect the custom JSON encoder.

## Why did my alias not appear in output?

Aliases are used for input by default. Enable one of:

- `Config.serialize_by_alias = True`
- `TO_DICT_ADD_BY_ALIAS_FLAG`, then `to_dict(by_alias=True)`
- A dialect with `serialize_by_alias = True`

The alias may come from field metadata, `Annotated[..., Alias(...)]`, or `Config.aliases` in that precedence order.

## Why was `None` not omitted in a nested model?

A dynamic `omit_none=True` flag only propagates through nested converters that support the option. Put `TO_DICT_ADD_OMIT_NONE_FLAG` on a shared base config or use fixed `omit_none=True` on the nested model/dialect.

## Why is TOML different from `to_dict()`?

[TOML](https://toml.io/en/v1.0.0) has no null and has native date/time types. Its built-in dialect omits `None` and passes date/time objects through to `tomli-w`. This is deliberate format behavior, not a failed basic round trip.

## Debugging workflow

- Reduce the failure to `to_dict()`/`from_dict()` or a Basic codec first.
- Print the exact annotated shape passed to the codec.
- Enable `Config.debug=True` to inspect generated code.
- Check field metadata, then model config, then active dialect.
- Verify custom serialize/deserialize functions are true inverses.
- Test the final format's constraints independently.
- Reproduce under the oldest and newest supported Python versions if annotations are involved.
- Turn the reproduction into a focused test before changing configuration.

## Boundary error handling

At an HTTP or message-consumer boundary, a useful pattern is:

```python
from mashumaro.exceptions import (
    ExtraKeysError,
    InvalidFieldValue,
    MissingDiscriminatorError,
    MissingField,
    SuitableVariantNotFoundError,
)


INPUT_ERRORS = (
    MissingField,
    ExtraKeysError,
    InvalidFieldValue,
    MissingDiscriminatorError,
    SuitableVariantNotFoundError,
)
```

Treat configuration exceptions such as `UnserializableField`, `BadHookSignature`, and `BadDialect` as deployment/programming failures rather than malformed user input.
