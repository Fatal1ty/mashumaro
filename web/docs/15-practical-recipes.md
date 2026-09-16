---
title: Practical Recipes
group: Guides
---

# Practical Recipes

These patterns combine the lower-level features into common application contracts. Each recipe keeps typed conversion, wire representation, and compatibility policy explicit.

## Camel-case API fields

For a small stable model, declare aliases directly:

```python
from dataclasses import dataclass
from typing import Annotated

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig
from mashumaro.types import Alias


@dataclass
class APIUser(DataClassDictMixin):
    user_id: Annotated[int, Alias("userId")]
    display_name: Annotated[str, Alias("displayName")]

    class Config(BaseConfig):
        serialize_by_alias = True
        allow_deserialization_not_by_alias = True


user = APIUser.from_dict({"userId": 42, "displayName": "Alice"})
assert user.to_dict() == {"userId": 42, "displayName": "Alice"}
```

Mashumaro deliberately uses an explicit alias mapping rather than guessing a naming convention. For a generated model set, create the `Config.aliases` dictionaries in your model-generation layer and snapshot-test them.

## Rename a field without breaking old payloads

An alias plus `allow_deserialization_not_by_alias` supports two names: the external alias and current Python field name.

For more than two historical names, normalize them before deserialization:

```python
from dataclasses import dataclass

from mashumaro import DataClassDictMixin


@dataclass
class Customer(DataClassDictMixin):
    display_name: str

    @classmethod
    def __pre_deserialize__(cls, data):
        data = dict(data)
        for old_name in ("name", "full_name", "displayName"):
            if old_name in data and "display_name" not in data:
                data["display_name"] = data.pop(old_name)
        return data
```

Choose one canonical output name and stop emitting old names. Input compatibility can be wider than output compatibility.

## Strict public payload, flexible internal model

Use a boundary wrapper with strict keys while keeping reusable nested domain objects permissive:

```python
from dataclasses import dataclass

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig


@dataclass
class Address:
    city: str
    postal_code: str


@dataclass
class CreateUserRequest(DataClassDictMixin):
    name: str
    address: Address

    class Config(BaseConfig):
        forbid_extra_keys = True
```

Strictness on the root catches request typos. Add strict config to nested types too if unknown nested fields must be rejected.

## Partial updates with `TypedDict`

A dataclass describes a constructible object and normally requires fields without defaults. A non-total [`TypedDict`](https://docs.python.org/3/library/typing.html#typing.TypedDict) is a better shape for PATCH-style data:

```python
from typing import TypedDict

from mashumaro.codecs.json import JSONDecoder


class UserPatch(TypedDict, total=False):
    display_name: str
    age: int
    active: bool


decode_patch = JSONDecoder(UserPatch)
patch = decode_patch.decode('{"age": "31"}')

assert patch == {"age": 31}
```

Apply the resulting keys to your domain object in a separate update layer where authorization and business validation live.

## Unix timestamps

```python
from dataclasses import dataclass
from datetime import datetime, timezone

from mashumaro import DataClassDictMixin
from mashumaro.types import SerializationStrategy


class UTCUnixTimestamp(
    SerializationStrategy, use_annotations=True
):
    def serialize(self, value: datetime) -> float:
        if value.tzinfo is None:
            raise ValueError("timezone-aware datetime required")
        return value.timestamp()

    def deserialize(self, value: float) -> datetime:
        return datetime.fromtimestamp(value, tz=timezone.utc)


@dataclass
class Event(DataClassDictMixin):
    at: datetime

    class Config:
        serialization_strategy = {datetime: UTCUnixTimestamp()}
```

Requiring [aware datetimes](https://docs.python.org/3/library/datetime.html#aware-and-naive-objects) avoids machine-local timezone behavior. The strategy uses [`datetime.timestamp()`](https://docs.python.org/3/library/datetime.html#datetime.datetime.timestamp) and [`datetime.fromtimestamp()`](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromtimestamp); document whether fractional seconds are allowed and whether the number is seconds or milliseconds.

## URL-safe Base64 without newlines

```python
import base64
from dataclasses import dataclass

from mashumaro import DataClassDictMixin
from mashumaro.dialect import Dialect


class URLSafeBase64Dialect(Dialect):
    serialization_strategy = {
        bytes: {
            "serialize": lambda value: base64.urlsafe_b64encode(value).decode(
                "ascii"
            ),
            "deserialize": lambda value: base64.urlsafe_b64decode(
                value.encode("ascii")
            ),
        }
    }


@dataclass
class Token(DataClassDictMixin):
    raw: bytes

    class Config:
        dialect = URLSafeBase64Dialect


token = Token(b"\xfb\xff")
assert token.to_dict() == {"raw": "-_8="}
assert Token.from_dict(token.to_dict()) == token
```

This replaces the default Base64 encoder that includes a trailing newline with [`base64.urlsafe_b64encode()`](https://docs.python.org/3/library/base64.html#base64.urlsafe_b64encode) and [`base64.urlsafe_b64decode()`](https://docs.python.org/3/library/base64.html#base64.urlsafe_b64decode).

## Public and internal representations

Use dialects instead of duplicate models when fields are identical but scalar representation differs:

```python
from datetime import date

from mashumaro.dialect import Dialect


class PublicDialect(Dialect):
    serialization_strategy = {
        date: {
            "serialize": date.isoformat,
            "deserialize": date.fromisoformat,
        }
    }
    omit_none = True


class StorageDialect(Dialect):
    serialization_strategy = {
        date: {
            "serialize": date.toordinal,
            "deserialize": date.fromordinal,
        }
    }
    omit_none = False
```

Enable `ADD_DIALECT_SUPPORT` for call-time selection, or construct separate codecs with different `default_dialect` values.

## Context-aware redaction

```python
from dataclasses import dataclass

from mashumaro import DataClassDictMixin
from mashumaro.config import ADD_SERIALIZATION_CONTEXT, BaseConfig


@dataclass
class Account(DataClassDictMixin):
    username: str
    email: str
    api_key: str

    class Config(BaseConfig):
        code_generation_options = [ADD_SERIALIZATION_CONTEXT]

    def __post_serialize__(self, data, context=None):
        audience = (context or {}).get("audience", "internal")
        if audience == "public":
            data.pop("email")
            data.pop("api_key")
        elif audience == "support":
            data["api_key"] = "***"
        return data
```

For a field that must never leave the process, prefer `serialize="omit"`. Context redaction is appropriate only when multiple explicitly tested audiences are a real requirement.

## Versioned event envelopes

Keep protocol versioning separate from variant tagging:

```python
from dataclasses import dataclass
from typing import Annotated, Literal

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig
from mashumaro.types import Discriminator


@dataclass
class UserCreated:
    type: Literal["user.created"] = "user.created"
    user_id: int = 0


@dataclass
class UserDeleted:
    type: Literal["user.deleted"] = "user.deleted"
    user_id: int = 0


Event = Annotated[
    UserCreated | UserDeleted,
    Discriminator(field="type", include_supertypes=True),
]


@dataclass
class Envelope(DataClassDictMixin):
    schema_version: Literal[1]
    event: Event

    class Config(BaseConfig):
        forbid_extra_keys = True
```

The [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal) version selects an envelope migration; the discriminator selects an event class. Keep tag values stable and add a new version when representation meaning changes incompatibly.

## Human-readable JSON with standard library

```python
import json
from functools import partial

pretty_json = partial(
    json.dumps,
    indent=2,
    sort_keys=True,
    ensure_ascii=False,
)

text = model.to_json(encoder=pretty_json)
```

The example binds options with [`functools.partial`](https://docs.python.org/3/library/functools.html#functools.partial) and passes them to [`json.dumps`](https://docs.python.org/3/library/json.html#json.dumps). For codecs:

```python
from mashumaro.codecs.json import JSONEncoder

encoder = JSONEncoder(Model, post_encoder_func=pretty_json)
```

The callable receives Mashumaro's basic form, so normal typed conversion is preserved.

## Decimal money as fixed strings

```python
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_EVEN

from mashumaro import DataClassDictMixin, field_options
from mashumaro.types import RoundedDecimal


@dataclass
class LineItem(DataClassDictMixin):
    total: Decimal = field(
        metadata=field_options(
            serialization_strategy=RoundedDecimal(
                places=2, rounding=ROUND_HALF_EVEN
            )
        )
    )
```

Rounding at serialization does not mutate the in-memory [`Decimal`](https://docs.python.org/3/library/decimal.html#decimal.Decimal). The [`ROUND_HALF_EVEN`](https://docs.python.org/3/library/decimal.html#decimal.ROUND_HALF_EVEN) mode resolves halfway cases toward the nearest even value. Decide whether deserialized values must already have the same scale and validate that rule separately.

## Codec adapter around an existing parser

If a framework already parses the transport, use a Basic codec:

```python
from mashumaro.codecs.basic import BasicDecoder, BasicEncoder

request_decoder = BasicDecoder(CreateUserRequest)
response_encoder = BasicEncoder(APIUser)

request = request_decoder.decode(framework_request_json)
framework_response_json = response_encoder.encode(response_model)
```

This avoids encoding JSON to text and parsing it again just to reach the typed conversion layer.

## Compatibility tests

For a durable contract, test exact representations in both directions:

```python
def test_user_wire_contract():
    wire = {"userId": 42, "displayName": "Alice"}
    model = APIUser(42, "Alice")

    assert APIUser.from_dict(wire) == model
    assert model.to_dict() == wire
```

Add fixtures from previous released versions, unknown keys/tags, missing optional fields, and boundary numeric/date values. Round-trip equality alone can miss an unintended but symmetrical wire-format change.
