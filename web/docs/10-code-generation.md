---
title: Code Generation Options
group: Advanced
---

# Code Generation Options

Mashumaro keeps common generated methods small. Features that add runtime branches or method parameters are enabled through `Config.code_generation_options`.

## Available flags

| Constant | Generated behavior |
|---|---|
| `TO_DICT_ADD_OMIT_NONE_FLAG` | Adds `omit_none=` to serialization methods |
| `TO_DICT_ADD_BY_ALIAS_FLAG` | Adds `by_alias=` to serialization methods |
| `ADD_DIALECT_SUPPORT` | Adds `dialect=` to serialization and deserialization methods |
| `ADD_SERIALIZATION_CONTEXT` | Adds `context=` to serialization methods and hooks |

```python
from mashumaro.config import (
    ADD_DIALECT_SUPPORT,
    ADD_SERIALIZATION_CONTEXT,
    TO_DICT_ADD_BY_ALIAS_FLAG,
    TO_DICT_ADD_OMIT_NONE_FLAG,
    BaseConfig,
)
```

Calling one of these keyword arguments without enabling its flag raises normal [`TypeError`](https://docs.python.org/3/library/exceptions.html#TypeError) because the generated method does not accept it.

## Dynamic `omit_none`

```python
from dataclasses import dataclass

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig, TO_DICT_ADD_OMIT_NONE_FLAG


@dataclass
class SearchResult(DataClassDictMixin):
    title: str
    snippet: str | None = None

    class Config(BaseConfig):
        code_generation_options = [TO_DICT_ADD_OMIT_NONE_FLAG]


result = SearchResult("Mashumaro")
assert result.to_dict() == {"title": "Mashumaro", "snippet": None}
assert result.to_dict(omit_none=True) == {"title": "Mashumaro"}
```

The no-argument default comes from `Config.omit_none` or the active dialect. The explicit call value overrides that default:

```python
class Config(BaseConfig):
    omit_none = True
    code_generation_options = [TO_DICT_ADD_OMIT_NONE_FLAG]

# to_dict() omits None; to_dict(omit_none=False) includes it
```

## Dynamic aliases

```python
from dataclasses import dataclass, field

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig, TO_DICT_ADD_BY_ALIAS_FLAG


@dataclass
class User(DataClassDictMixin):
    user_id: int = field(metadata={"alias": "userId"})

    class Config(BaseConfig):
        code_generation_options = [TO_DICT_ADD_BY_ALIAS_FLAG]


user = User(42)
assert user.to_dict() == {"user_id": 42}
assert user.to_dict(by_alias=True) == {"userId": 42}
```

If `serialize_by_alias=True`, the no-argument result uses aliases and `by_alias=False` temporarily restores Python names.

## Dynamic dialects

`ADD_DIALECT_SUPPORT` adds `dialect=` to `to_dict()`, `from_dict()`, and format-specific mixin methods:

```python
from dataclasses import dataclass
from datetime import date

from mashumaro import DataClassDictMixin
from mashumaro.config import ADD_DIALECT_SUPPORT, BaseConfig


@dataclass
class Release(DataClassDictMixin):
    day: date

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]


wire = Release(date(2026, 8, 16)).to_dict(
    dialect=OrdinalStorageDialect
)
assert Release.from_dict(wire, dialect=OrdinalStorageDialect) == Release(
    date(2026, 8, 16)
)
```

See [Dialects](#/docs/dialects) for model and codec defaults.

## Serialization context

`ADD_SERIALIZATION_CONTEXT` adds a caller-defined `context` value and passes it to `__pre_serialize__` and `__post_serialize__` hooks that accept the extra parameter. [`Any`](https://docs.python.org/3/library/typing.html#typing.Any) is convenient for open-ended examples, but applications can annotate a `TypedDict`, protocol, or mapping for a stricter context contract.

```python
from dataclasses import dataclass
from typing import Any

from mashumaro import DataClassDictMixin
from mashumaro.config import ADD_SERIALIZATION_CONTEXT, BaseConfig


@dataclass
class Account(DataClassDictMixin):
    username: str
    email: str

    class Config(BaseConfig):
        code_generation_options = [ADD_SERIALIZATION_CONTEXT]

    def __post_serialize__(
        self, data: dict[str, Any], context: dict | None = None
    ) -> dict[str, Any]:
        if context and context.get("public"):
            data.pop("email")
        return data


account = Account("alice", "alice@example.com")
assert account.to_dict(context={"public": True}) == {
    "username": "alice"
}
```

Context is serialization-only. Deserialization hooks do not receive it. The context type and mutation policy belong to your application; a small immutable [`Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping) is often easiest to reason about.

## Combine flags

Options compose in a single keyword-only call:

```python
class Config(BaseConfig):
    code_generation_options = [
        TO_DICT_ADD_OMIT_NONE_FLAG,
        TO_DICT_ADD_BY_ALIAS_FLAG,
        ADD_DIALECT_SUPPORT,
        ADD_SERIALIZATION_CONTEXT,
    ]


data = model.to_dict(
    omit_none=True,
    by_alias=True,
    dialect=PublicAPIDialect,
    context={"public": True},
)
```

## Nested propagation

Dynamic flags propagate only where the nested generated converter supports the same feature. This distinction is deliberate:

```python
from dataclasses import dataclass


@dataclass
class Inner(DataClassDictMixin):
    value: int | None = None


@dataclass
class Outer(DataClassDictMixin):
    inner: Inner
    value: int | None = None

    class Config(BaseConfig):
        code_generation_options = [TO_DICT_ADD_OMIT_NONE_FLAG]


assert Outer(Inner()).to_dict(omit_none=True) == {
    "inner": {"value": None}
}
```

`Outer.value` is omitted, while `Inner.value` remains because `Inner` did not opt into the dynamic flag. Add the option to a shared base config when an entire model graph should honor it.

The same principle prevents a parent call from silently changing a nested model that intentionally has a different external contract.

## Performance guidance

Each option adds generated code and sometimes a branch per call. The cost is usually small, but do not enable every option globally without a use case. Fixed `Config` or dialect values produce a simpler API when behavior never changes at runtime.
