---
title: Getting Started
---

# Getting Started

Mashumaro is a fast serialization library built around [Python type annotations](https://docs.python.org/3/library/typing.html) and [dataclasses](https://docs.python.org/3/library/dataclasses.html). It generates specialized packing and unpacking functions for your exact type shape, so the normal hot path does not repeatedly inspect fields or walk annotations.

Use a **mixin** when the root object is a dataclass and methods such as `to_json()` are the most convenient API. Use a reusable **codec** when the root shape is anything else — for example `list[User]`, `dict[str, Event | None]`, a `TypedDict`, or a scalar type.

## Installation and Python compatibility

Install the [mashumaro package from PyPI](https://pypi.org/project/mashumaro/) with [pip](https://pip.pypa.io/en/stable/cli/pip_install/):

```bash
pip install mashumaro
```

Mashumaro {{PACKAGE_VERSION}} supports **Python {{PYTHON_VERSION_RANGE}}**. For older Python versions, use the last compatible Mashumaro release listed below.

| Python | Recommended mashumaro version | Status |
|---|---|---|
| {{PYTHON_VERSION_RANGE}} | Current release | Supported |
| 3.9 | 3.20 | Last compatible release |
| 3.8 | 3.14 | Last compatible release |
| 3.7 | 3.9.1 | Last compatible release |
| 3.6 | 3.1.1 | Last compatible release |

A Python version that has reached [end of life](https://devguide.python.org/versions/) no longer receives fixes from CPython. Pinning an old mashumaro release preserves compatibility, but upgrading Python is the safer choice.

The dictionary and standard-library JSON APIs need no extra dependencies. Install only the [package extras](https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-extras) required by your wire formats:

```bash
pip install "mashumaro[orjson]"
pip install "mashumaro[yaml]"
pip install "mashumaro[toml]"
pip install "mashumaro[msgpack]"

# Multiple extras may be installed together
pip install "mashumaro[orjson,yaml,toml,msgpack]"
```

| Extra | Dependency | What it enables |
|---|---|---|
| `orjson` | [`orjson`](https://pypi.org/project/orjson/) | Fast JSON bytes and the orjson mixin/codec |
| `yaml` | [`PyYAML`](https://pypi.org/project/PyYAML/) | YAML mixin and codec |
| `toml` | [`tomli-w`](https://pypi.org/project/tomli-w/), plus [`tomli`](https://pypi.org/project/tomli/) on Python 3.10 | TOML mixin and codec |
| `msgpack` | [`msgpack`](https://pypi.org/project/msgpack/) | MessagePack mixin and codec |

## Your first model

Declare ordinary dataclasses and add a mixin only to the root model that needs serialization methods. Nested dataclasses do not need to inherit a mixin.

```python
from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from mashumaro.mixins.json import DataClassJSONMixin


@dataclass
class Address:
    city: str
    postal_code: str


@dataclass
class User(DataClassJSONMixin):
    id: UUID
    name: str
    address: Address
    created_at: datetime
    tags: list[str]


user = User(
    id=UUID("20f16666-90f3-4d73-a034-4e73a57e8f30"),
    name="Alice",
    address=Address(city="Belgrade", postal_code="11000"),
    created_at=datetime(2026, 8, 16, 12, 30, tzinfo=timezone.utc),
    tags=["admin", "beta"],
)

payload = user.to_json()
restored = User.from_json(payload)

assert restored == user
```

The same model also has `to_dict()` and `from_dict()` because every format-specific mixin derives from `DataClassDictMixin`:

```python
basic = user.to_dict()

assert basic["id"] == "20f16666-90f3-4d73-a034-4e73a57e8f30"
assert basic["address"] == {"city": "Belgrade", "postal_code": "11000"}
assert User.from_dict(basic) == user
```

`to_dict()` does not mean [`dataclasses.asdict()`](https://docs.python.org/3/library/dataclasses.html#dataclasses.asdict). Mashumaro converts values according to their annotations: UUIDs and dates become strings, sets become lists, nested dataclasses become dictionaries, and custom strategies are applied.

## Mixins or codecs?

Both APIs use the same generated conversion engine. Choose the entry point that expresses the root shape most naturally.

| Question | Mixin | Codec |
|---|---|---|
| Root value | Dataclass instance | Any supported type shape |
| API | Methods on the model | Reusable encoder/decoder object |
| Compile time | Class creation, or first use with lazy compilation | Codec construction |
| Best fit | Application/domain models | Collections, scalars, adapters, framework boundaries |

### Mixin example

```python
from dataclasses import dataclass

from mashumaro.mixins.json import DataClassJSONMixin


@dataclass
class ServiceConfig(DataClassJSONMixin):
    host: str
    port: int
    debug: bool = False


config = ServiceConfig(host="localhost", port=8080)
text = config.to_json()
assert ServiceConfig.from_json(text) == config
```

### Codec example

A codec takes the entire **shape type** at construction time. Build it once and reuse it when performance matters.

```python
from mashumaro.codecs.json import JSONDecoder, JSONEncoder

encoder = JSONEncoder(list[ServiceConfig])
decoder = JSONDecoder(list[ServiceConfig])

configs = [
    ServiceConfig("api.internal", 443),
    ServiceConfig("worker.internal", 8080, True),
]

payload = encoder.encode(configs)
assert decoder.decode(payload) == configs
```

For a one-off conversion, each codec module also exposes functions:

```python
from mashumaro.codecs.json import decode, encode

payload = encode(configs, list[ServiceConfig])
restored = decode(payload, list[ServiceConfig])
```

These functions create a disposable codec internally. Reuse an encoder or decoder for repeated work so code generation happens once.

## The serialization pipeline

It helps to distinguish three layers:

- **Typed object** — the value your application uses, such as `User` or `list[User]`.
- **Basic form** — dictionaries, lists, and scalar values produced by Mashumaro's generated packer.
- **Encoded payload** — JSON text, YAML text, TOML text, or MessagePack bytes produced by the format library.

For JSON encoding, the flow is:

```text
User -> generated packer -> dict/list/scalars -> json.dumps -> str
str -> json.loads -> dict/list/scalars -> generated unpacker -> User
```

Format dialects can deliberately keep native values in the basic form. For example, MessagePack keeps `bytes`, TOML keeps native `date`/`time`/`datetime`, and orjson handles several native scalar types itself. The [Supported Types](#/docs/supported-types) chapter documents these differences.

## Conversion and validation

Deserialization is annotation-directed conversion, not merely assignment:

```python
from dataclasses import dataclass
from datetime import date

from mashumaro import DataClassDictMixin


@dataclass
class Invoice(DataClassDictMixin):
    number: int
    issued_on: date
    paid: bool


invoice = Invoice.from_dict(
    {"number": "42", "issued_on": "2026-08-16", "paid": 1}
)

assert invoice == Invoice(42, date(2026, 8, 16), True)
```

When conversion fails, Mashumaro raises a typed exception such as `InvalidFieldValue`; missing and unexpected keys have separate exceptions. See [Errors and Troubleshooting](#/docs/errors-and-troubleshooting).

Mashumaro is not a business-rule validator. Constraints such as “price must be positive” belong in your model, a validation layer, or generated [JSON Schema](#/docs/json-schema). Serialization hooks can normalize data but should not hide invalid domain states.

## Recommended project pattern

For a medium or large codebase:

- Put shared defaults in a project base mixin with an inner `Config`.
- Keep wire-format choices at system boundaries.
- Use field options for genuinely local exceptions.
- Use reusable `SerializationStrategy` objects for third-party types.
- Use dialects when the same model must speak more than one external representation.
- Reuse codecs for repeated serialization of the same root shape.
- Enable `forbid_extra_keys` at strict API boundaries.

```python
from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig


class APIModel(DataClassDictMixin):
    class Config(BaseConfig):
        forbid_extra_keys = True
        allow_deserialization_not_by_alias = True
```

Configuration is inherited, and a dataclass can override only the options it needs.

## Where to go next

- [Supported Formats](#/docs/supported-formats) lists every mixin, codec, function, dependency, and return type.
- [Supported Types](#/docs/supported-types) is the complete representation and Python-version reference.
- [Field Options](#/docs/field-options) and [Config Options](#/docs/config-options) cover local and model-wide behavior.
- [SerializationStrategy](#/docs/serializationstrategy) and [SerializableType](#/docs/serializabletype) add third-party and user-owned types.
- [Discriminator](#/docs/discriminator) covers polymorphic models.
- [JSON Schema](#/docs/json-schema) covers Draft 2020-12 and OpenAPI 3.1 schema generation.
