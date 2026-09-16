---
title: Serialization Hooks
group: Advanced
---

# Serialization Hooks

Hooks intercept a dataclass at four points around generated conversion. They work through dictionary and format mixins and when the dataclass is nested inside a codec shape.

## Lifecycle

| Hook | Required kind | Input | Must return |
|---|---|---|---|
| `__pre_deserialize__` | [`classmethod`](https://docs.python.org/3/library/functions.html#classmethod) | Raw mapping | Mapping to unpack |
| `__post_deserialize__` | [`classmethod`](https://docs.python.org/3/library/functions.html#classmethod) | Constructed instance | Final instance |
| `__pre_serialize__` | Instance method | `self` | Instance to pack |
| `__post_serialize__` | Instance method | Packed dictionary | Final dictionary |

With serialization context enabled, the two serialization hooks may also accept `context`.

## Before deserialization

Normalize or migrate raw keys before field lookup:

```python
from dataclasses import dataclass
from typing import Any

from mashumaro.mixins.json import DataClassJSONMixin


@dataclass
class User(DataClassJSONMixin):
    name: str
    age: int

    @classmethod
    def __pre_deserialize__(
        cls, data: dict[str, Any]
    ) -> dict[str, Any]:
        normalized = {key.lower(): value for key, value in data.items()}
        if "years" in normalized and "age" not in normalized:
            normalized["age"] = normalized.pop("years")
        return normalized


assert User.from_json('{"NAME": "Alice", "years": "30"}') == User(
    "Alice", 30
)
```

The hook runs after the format parser has produced a [`Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping) but before typed field conversion. It can therefore rename keys and reshape input while leaving date/enum/nested conversion to Mashumaro.

## After deserialization

Inspect or replace the fully constructed object:

```python
from dataclasses import dataclass

from mashumaro import DataClassDictMixin


@dataclass
class Score(DataClassDictMixin):
    value: int

    @classmethod
    def __post_deserialize__(cls, obj: "Score") -> "Score":
        obj.value = max(0, min(100, obj.value))
        return obj


assert Score.from_dict({"value": 120}) == Score(100)
```

This hook receives an instance whose fields already have their annotated runtime types. Returning an instance is mandatory; it may be the same object or a replacement compatible with the class contract.

## Before serialization

Select or prepare the object before generated field packing:

```python
from dataclasses import dataclass
from typing import ClassVar

from mashumaro import DataClassDictMixin


@dataclass
class Metered(DataClassDictMixin):
    value: int
    serializations: ClassVar[int] = 0

    def __pre_serialize__(self) -> "Metered":
        type(self).serializations += 1
        return self
```

[`ClassVar`](https://docs.python.org/3/library/typing.html#typing.ClassVar) keeps the counter out of the dataclass field set. Avoid mutating ordinary instance fields just to serialize them: repeated calls should usually produce the same result. A strategy or `__post_serialize__` transformation is easier to reason about for pure representation changes.

## After serialization

Transform the complete dictionary after all fields have been packed:

```python
from dataclasses import dataclass
from typing import Any

from mashumaro import DataClassDictMixin


@dataclass
class Credentials(DataClassDictMixin):
    username: str
    password: str

    def __post_serialize__(
        self, data: dict[str, Any]
    ) -> dict[str, Any]:
        data.pop("password")
        data["kind"] = "credentials"
        return data


assert Credentials("alice", "secret").to_dict() == {
    "username": "alice",
    "kind": "credentials",
}
```

For a field that must never be emitted, `serialize="omit"` is more explicit. A post hook is best for transformations that need multiple fields or the complete mapping.

## Serialization context

Enable `ADD_SERIALIZATION_CONTEXT` to make per-call policy available to serialization hooks:

```python
from dataclasses import dataclass
from typing import Any

from mashumaro import DataClassDictMixin
from mashumaro.config import ADD_SERIALIZATION_CONTEXT, BaseConfig


@dataclass
class Profile(DataClassDictMixin):
    username: str
    email: str

    class Config(BaseConfig):
        code_generation_options = [ADD_SERIALIZATION_CONTEXT]

    def __pre_serialize__(
        self, context: dict[str, Any] | None = None
    ) -> "Profile":
        return self

    def __post_serialize__(
        self,
        data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if context and context.get("audience") == "public":
            data.pop("email")
        return data


profile = Profile("alice", "alice@example.com")
assert profile.to_dict(context={"audience": "public"}) == {
    "username": "alice"
}
```

Context propagates through nested models whose generated methods support it. Models without the option keep their ordinary hook signature and behavior.

## Hook inheritance

Hooks can be defined in a parent class and are discovered on descendants:

```python
class LowercaseInput:
    @classmethod
    def __pre_deserialize__(cls, data):
        return {key.lower(): value for key, value in data.items()}


@dataclass
class Model(LowercaseInput, DataClassDictMixin):
    value: int
```

This is useful for cross-cutting migrations, but a base hook affects every descendant. Keep it generic and test inheritance combinations.

## Signature validation

Mashumaro validates whether pre/post deserialization hooks are classmethods and whether hook signatures match the enabled features. Invalid definitions raise `BadHookSignature` during class processing instead of failing much later in a request.

Correct signatures are:

```python
@classmethod
def __pre_deserialize__(cls, data): ...

@classmethod
def __post_deserialize__(cls, obj): ...

def __pre_serialize__(self): ...

def __post_serialize__(self, data): ...
```

With context, add an optional second argument to pre-serialize and third argument to post-serialize as shown above.

## Hooks versus other extensions

| Requirement | Prefer |
|---|---|
| Convert one field | Field callable or strategy |
| Convert every value of a type | Config strategy |
| Switch representation by destination | Dialect |
| Rename one key | Alias |
| Migrate or reshape a whole old payload | Pre-deserialize hook |
| Add/remove output based on several fields | Post-serialize hook |
| Choose a polymorphic class | Discriminator |

Hooks are powerful because they see broad state. Use the narrowest extension that expresses the rule; narrow rules produce better schemas and fewer surprising interactions.
