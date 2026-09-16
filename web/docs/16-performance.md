---
title: Performance
group: Guides
---

# Performance

Mashumaro generates specialized Python functions for a concrete type shape. After compilation, conversion runs through direct code tailored to those fields and type arguments instead of repeatedly inspecting dataclasses and annotations.

## When compilation happens

| API | Default compilation point |
|---|---|
| Dataclass mixin | Class creation/import time |
| Mixin with `lazy_compilation=True` | First serialization/deserialization call |
| Reusable codec | Encoder/decoder construction |
| One-off codec function | Every function call creates a disposable codec |

This gives two distinct performance dimensions: setup latency and steady-state throughput.

## Reuse codecs

The most important optimization for non-dataclass roots is to construct once:

```python
from mashumaro.codecs.json import JSONDecoder, JSONEncoder

encoder = JSONEncoder(list[Event])
decoder = JSONDecoder(list[Event])


def publish(events: list[Event]) -> str:
    return encoder.encode(events)


def consume(payload: str) -> list[Event]:
    return decoder.decode(payload)
```

The convenient module functions are appropriate for one-time scripts:

```python
from mashumaro.codecs.json import encode

payload = encode(events, list[Event])
```

Do not call a one-off function repeatedly for the same shape on a hot path; it regenerates a codec each time.

## Eager versus lazy mixins

Eager compilation makes the first call fast and catches unsupported fields early. Lazy compilation reduces import work when an application declares many models but uses few of them:

```python
class Config(BaseConfig):
    lazy_compilation = True
```

Choose based on application startup behavior:

- CLI/serverless workloads may benefit from lazy models that are rarely touched.
- Long-running services usually benefit from eager failure and predictable first-request latency.
- If you choose lazy compilation, warm critical models during startup when latency spikes are unacceptable.

Measure total startup plus first-use cost; import time alone can hide deferred work.

## Choose the format deliberately

The typed conversion stage and the final encoder both contribute to runtime.

| Requirement | Candidate |
|---|---|
| No dependency, maximum compatibility | Standard-library JSON |
| High JSON throughput, bytes output | orjson |
| Compact binary internal payload | MessagePack |
| Human-edited configuration | TOML or YAML; optimize readability first |
| Framework already parsed JSON | Basic encoder/decoder to avoid re-encoding |

[orjson](https://github.com/ijl/orjson) can encode `datetime`, `date`, `time`, and `UUID` natively through its built-in dialect. [MessagePack](https://msgpack.org/) keeps bytes native. These paths can avoid intermediate conversions as well as using a faster final encoder.

Benchmark with your real shapes: deeply nested unions, large primitive lists, custom strategies, and many optional fields stress different parts of the pipeline.

## Avoid unnecessary copies carefully

Dialect `no_copy_collections` can pass selected collection types through:

```python
class InternalDialect(Dialect):
    no_copy_collections = (list, dict)
```

Use it only when elements need no conversion and the downstream consumer will not mutate input. Eliminating a shallow copy is valuable for large containers but irrelevant for small models, and aliasing mutable objects can be far more expensive than the allocation it saved.

Built-in orjson, TOML, and MessagePack dialects already select safe native-container paths for their encoders.

## Prefer fixed behavior when it is fixed

Dynamic code-generation flags add per-call parameters and branches. If a model always omits `None`, use:

```python
class Config(BaseConfig):
    omit_none = True
```

Enable `TO_DICT_ADD_OMIT_NONE_FLAG` only when callers genuinely switch behavior. The same applies to aliases and dialect selection.

This is a small optimization, but it also produces a simpler and more stable API.

## Tagged unions scale better

An untagged union or discriminator may try multiple variants until one succeeds. A field discriminator maps a tag directly to the intended variant:

```python
Discriminator(field="type", include_subtypes=True)
```

The benefit grows with the number and overlap of variants. Tagged payloads also make failure deterministic and easier to debug.

## Custom strategy costs

Strategies are compiled into generated calls, but the callable's work still matters.

- Reuse immutable strategy instances instead of allocating them per value.
- Avoid reparsing constant format strings or calling [`re.compile()`](https://docs.python.org/3/library/re.html#re.compile) inside `serialize()`.
- Use annotation processing only when recursive conversion is needed.
- Return the final simple representation directly when possible.
- Keep hooks free of network, disk, and global-lock operations.

A Python lambda and a strategy method have similar call overhead in the hot path; choose the clearer reusable design first, then profile.

## Omission and payload size

`omit_none` and `omit_default` reduce output size and final encoder work, but equality checks and default-factory evaluation have a cost. They are most useful for sparse models and network/storage payloads, not as a blanket micro-optimization.

Do not change omission policy only for speed if consumers distinguish missing from explicit null/default.

## Sorting keys

`sort_keys=True` creates deterministic dictionary order but adds sorting work. Enable it for reproducible snapshots, signatures, or human comparison; leave it off on throughput-sensitive paths that do not require canonical ordering.

The final JSON encoder may sort again if configured separately. Avoid paying for both basic-form and encoder sorting unless nested model policy requires it.

## Measure correctly

A useful benchmark separates:

- Import/class construction.
- Codec construction.
- First lazy call.
- Repeated encode/decode.
- Typed conversion alone with Basic codecs.
- Final format encoding alone.
- Allocation/peak memory for large collections.

Use representative payloads and a benchmark runner such as [`pyperf`](https://pyperf.readthedocs.io/en/stable/); follow its [guidance for reproducible runs](https://pyperf.readthedocs.io/en/stable/run_benchmark.html) and use enough processes to reduce noise. Compare exact semantics — bytes versus strings, validation strictness, omission, aliases, datetime handling, and unknown keys — before comparing numbers.

The repository benchmark uses real nested models and logarithmic charts. Results are workload- and configuration-dependent, so treat published comparisons as orientation rather than a guarantee for your application.

## Performance checklist

- Reuse encoders and decoders.
- Avoid round-tripping through JSON when a framework already provides dictionaries.
- Pick eager or lazy compilation based on first-use latency.
- Use tagged discriminators for large polymorphic sets.
- Select orjson/MessagePack when their boundary contract fits.
- Benchmark before enabling `no_copy_collections`.
- Keep strategies and hooks deterministic and local.
- Test payload semantics before optimizing representation size.
