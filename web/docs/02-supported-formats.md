---
title: Supported Formats
---

# Supported Formats

Mashumaro provides a dictionary “basic form” plus JSON, orjson, YAML, TOML, and MessagePack integrations. Every integration has a reusable codec API; dataclass roots also have mixins with format-specific methods.

## API overview

| Format | Mixin methods | Reusable codec | One-off functions | Encoded result |
|---|---|---|---|---|
| Basic form | `to_dict`, `from_dict` | `BasicEncoder`, `BasicDecoder` | `encode`, `decode` | Python object |
| JSON | `to_json`, `from_json` | `JSONEncoder`, `JSONDecoder` | `json_encode`, `json_decode` | `str` by default |
| orjson | `to_jsonb`, `to_json`, `from_json` | `ORJSONEncoder`, `ORJSONDecoder` | `json_encode`, `json_decode` | `bytes` from encoder/`to_jsonb` |
| YAML | `to_yaml`, `from_yaml` | `YAMLEncoder`, `YAMLDecoder` | `yaml_encode`, `yaml_decode` | `str` or `bytes` |
| TOML | `to_toml`, `from_toml` | `TOMLEncoder`, `TOMLDecoder` | `toml_encode`, `toml_decode` | `str` |
| MessagePack | `to_msgpack`, `from_msgpack` | `MessagePackEncoder`, `MessagePackDecoder` | `msgpack_encode`, `msgpack_decode` | `bytes` |

Each module also exports its one-off functions as `encode` and `decode`, so an application can use a uniform import style.

## Basic form

The basic form is the typed conversion layer used underneath most other formats. It is also useful directly when passing values to a database driver, web framework, template renderer, or another serializer.

### Dataclass mixin

```python
from dataclasses import dataclass
from datetime import date

from mashumaro import DataClassDictMixin


@dataclass
class Release(DataClassDictMixin):
    version: str
    published: date


release = Release("1.0", date(2024, 1, 1))
assert release.to_dict() == {
    "version": "1.0",
    "published": "2024-01-01",
}
assert Release.from_dict(release.to_dict()) == release
```

Every format mixin derives from `DataClassDictMixin`, so do not inherit it separately when you already use `DataClassJSONMixin`, `DataClassYAMLMixin`, or another format mixin.

### Reusable and one-off codecs

```python
from mashumaro.codecs import BasicDecoder, BasicEncoder
from mashumaro.codecs.basic import decode, encode

shape = dict[str, list[Release]]
value = {"stable": [release]}

encoder = BasicEncoder(shape)
decoder = BasicDecoder(shape)

basic = encoder.encode(value)
assert decoder.decode(basic) == value
assert decode(encode(value, shape), shape) == value
```

`BasicDecoder` accepts an optional `pre_decoder_func`; `BasicEncoder` accepts `post_encoder_func`. These functions wrap the generated typed conversion and are useful for integrating a storage adapter without defining a new codec.

## Standard-library JSON

The standard JSON integration uses [`json.loads`](https://docs.python.org/3/library/json.html#json.loads) and [`json.dumps`](https://docs.python.org/3/library/json.html#json.dumps) by default and requires no extra package.

### Dataclass mixin

```python
from dataclasses import dataclass

from mashumaro.mixins.json import DataClassJSONMixin


@dataclass
class Point(DataClassJSONMixin):
    x: int
    y: int


text = Point(10, 20).to_json()
assert Point.from_json(text) == Point(10, 20)
```

`to_json()` accepts a replacement encoder as its first argument and forwards other keyword arguments to `to_dict()`. `from_json()` similarly accepts a decoder and forwards the rest to `from_dict()`.

```python
import json

pretty = Point(10, 20).to_json(
    encoder=lambda value: json.dumps(value, indent=2, sort_keys=True)
)
```

### Codec

```python
import json

from mashumaro.codecs.json import JSONDecoder, JSONEncoder

encoder = JSONEncoder(
    list[Point],
    post_encoder_func=lambda value: json.dumps(value, separators=(",", ":")),
)
decoder = JSONDecoder(list[Point])

payload = encoder.encode([Point(1, 2), Point(3, 4)])
assert decoder.decode(payload) == [Point(1, 2), Point(3, 4)]
```

The decoder accepts `str`, `bytes`, or `bytearray`. The default encoder returns `str`, but a custom `post_encoder_func` may define a different boundary contract.

### One-off functions

```python
from mashumaro.codecs.json import json_decode, json_encode

payload = json_encode(Point(1, 2), Point)
assert json_decode(payload, Point) == Point(1, 2)

# Equivalent short aliases
from mashumaro.codecs import json as json_codec

payload = json_codec.encode(Point(3, 4), Point)
assert json_codec.decode(payload, Point) == Point(3, 4)
```

## orjson

Install the optional dependency first:

```bash
pip install "mashumaro[orjson]"
```

The [orjson documentation](https://github.com/ijl/orjson) describes its bytes-oriented API and native types. orjson produces UTF-8 JSON bytes and natively handles `datetime`, `date`, `time`, and `UUID` on the serialization side. Mashumaro's `OrjsonDialect` passes those values through so orjson can encode them.

```python
from dataclasses import dataclass
from datetime import datetime, timezone

from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass
class AuditRecord(DataClassORJSONMixin):
    action: str
    at: datetime


record = AuditRecord("login", datetime(2026, 8, 16, tzinfo=timezone.utc))

binary_payload = record.to_jsonb()
text_payload = record.to_json()

assert isinstance(binary_payload, bytes)
assert isinstance(text_payload, str)
assert AuditRecord.from_json(binary_payload) == record
```

Use `Config.orjson_options` for a model-wide bitmask or pass `orjson_options=` to `to_jsonb()` for one call:

```python
import orjson

binary_payload = record.to_jsonb(
    orjson_options=orjson.OPT_INDENT_2 | orjson.OPT_SORT_KEYS
)
```

The reusable API is `ORJSONEncoder(shape)` and `ORJSONDecoder(shape)` from `mashumaro.codecs.orjson`. The encoder returns `bytes`; the one-off `json_encode` and `encode` functions do the same.

> orjson is not simply a drop-in speed flag for standard JSON. Its option set, return type, native-type handling, and error behavior come from orjson. Choose the integration as part of your external API contract.

## YAML

Install [PyYAML](https://pypi.org/project/PyYAML/):

```bash
pip install "mashumaro[yaml]"
```

```python
from dataclasses import dataclass

from mashumaro.mixins.yaml import DataClassYAMLMixin


@dataclass
class Pipeline(DataClassYAMLMixin):
    name: str
    steps: list[str]


pipeline = Pipeline("checks", ["lint", "test"])
yaml_text = pipeline.to_yaml()
assert Pipeline.from_yaml(yaml_text) == pipeline
```

Mashumaro selects [`CSafeLoader`](https://pyyaml.org/wiki/PyYAMLDocumentation#Loader) when available and falls back to [`SafeLoader`](https://pyyaml.org/wiki/PyYAMLDocumentation#Loader); for dumping it selects the C dumper when available. You can supply another encoder/decoder to the mixin or a `post_encoder_func`/`pre_decoder_func` to the codec:

```python
import yaml

from mashumaro.codecs.yaml import YAMLDecoder, YAMLEncoder

encoder = YAMLEncoder(
    Pipeline,
    post_encoder_func=lambda value: yaml.safe_dump(value, sort_keys=False),
)
decoder = YAMLDecoder(Pipeline, pre_decoder_func=yaml.safe_load)
```

Only load YAML from trusted or appropriately restricted sources. Mashumaro controls typed conversion after parsing; the safety characteristics of parsing are defined by the supplied PyYAML loader.

## TOML

Install the TOML extra:

```bash
pip install "mashumaro[toml]"
```

Python 3.11+ uses the standard-library [`tomllib`](https://docs.python.org/3/library/tomllib.html) for reading. Python 3.10 uses [`tomli`](https://pypi.org/project/tomli/). Writing uses [`tomli-w`](https://pypi.org/project/tomli-w/) on every supported Python version.

```python
from dataclasses import dataclass
from datetime import date

from mashumaro.mixins.toml import DataClassTOMLMixin


@dataclass
class AppConfig(DataClassTOMLMixin):
    title: str
    released: date
    description: str | None = None


config = AppConfig("Mashumaro", date(2026, 5, 26))
toml_text = config.to_toml()

assert "released = 2026-05-26" in toml_text
assert "description" not in toml_text
assert AppConfig.from_toml(toml_text) == config
```

[TOML 1.0](https://toml.io/en/v1.0.0) has native date/time values, so `TOMLDialect` passes `datetime`, `date`, and `time` through to `tomli-w`. TOML has no null value, so fields containing `None` are omitted by default. TOML documents are tables at the top level; use a dataclass or mapping-compatible shape rather than a scalar root.

Reusable codecs are `TOMLEncoder` and `TOMLDecoder`; one-off functions are `toml_encode`/`toml_decode` and their `encode`/`decode` aliases.

## MessagePack

Install [msgpack](https://pypi.org/project/msgpack/):

```bash
pip install "mashumaro[msgpack]"
```

```python
from dataclasses import dataclass

from mashumaro.mixins.msgpack import DataClassMessagePackMixin


@dataclass
class Blob(DataClassMessagePackMixin):
    media_type: str
    body: bytes


blob = Blob("application/octet-stream", b"\x00\x01\x02")
payload = blob.to_msgpack()

assert isinstance(payload, bytes)
assert Blob.from_msgpack(payload) == blob
```

`MessagePackDialect` passes `bytes` through and reconstructs `bytearray` explicitly. The default encoder calls [`msgpack.packb(..., use_bin_type=True)`](https://msgpack-python.readthedocs.io/en/stable/api.html#msgpack.packb) and the default decoder calls [`msgpack.unpackb(..., raw=False)`](https://msgpack-python.readthedocs.io/en/stable/api.html#msgpack.unpackb).

Use codec transforms to customize msgpack options without changing the typed layer:

```python
import msgpack

from mashumaro.codecs.msgpack import MessagePackDecoder, MessagePackEncoder

encoder = MessagePackEncoder(
    Blob,
    post_encoder_func=lambda value: msgpack.packb(value, use_bin_type=True),
)
decoder = MessagePackDecoder(
    Blob,
    pre_decoder_func=lambda value: msgpack.unpackb(value, raw=False),
)
```

## Custom format boundaries with codec transforms

All reusable codecs follow the same two-stage idea:

- A decoder's `pre_decoder_func` turns an encoded payload into the basic form before typed deserialization.
- An encoder's `post_encoder_func` turns the generated basic form into the final payload.

The basic codec permits `None` for either function; YAML and MessagePack do as well. This makes codecs useful even when another system already parses or renders the transport format.

```python
from urllib.parse import parse_qs, urlencode

from mashumaro.codecs.basic import BasicDecoder, BasicEncoder

query_encoder = BasicEncoder(
    dict[str, str], post_encoder_func=urlencode
)
query_decoder = BasicDecoder(
    dict[str, list[str]], pre_decoder_func=parse_qs
)

assert query_encoder.encode({"page": "2", "sort": "name"}) == (
    "page=2&sort=name"
)
assert query_decoder.decode("tag=python&tag=typing") == {
    "tag": ["python", "typing"]
}
```

The standard-library [`urllib.parse`](https://docs.python.org/3/library/urllib.parse.html) documentation defines the query-string behavior of `urlencode` and `parse_qs` used in this adapter.

## Choosing a format

| Need | Good default |
|---|---|
| Public interoperable API | Standard JSON |
| Maximum JSON throughput and bytes output | orjson |
| Human-edited nested configuration | YAML, with deliberate safe-loader policy |
| Human-edited application configuration with strict semantics | TOML |
| Compact internal binary messages | MessagePack |
| Already have a transport/storage adapter | Basic codec with transforms |

Serialization format does not replace a compatibility strategy. For durable data, define aliases, defaults, discriminators, and migration policy explicitly; test old payloads against new models.
