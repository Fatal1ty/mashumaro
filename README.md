<div align="center">

<img alt="mashumaro" width="175" src="https://raw.githubusercontent.com/Fatal1ty/mashumaro/ac2f924591d488dbd9a776a6b1ae7dede2d8c73e/img/logo.svg">

### High-performance serialization for standard Python types

Keep your dataclasses, `TypedDict`s, and type annotations. Mashumaro generates
specialized encoders and decoders for them — no hand-written schemas or model
framework required.

[![Build Status](https://github.com/Fatal1ty/mashumaro/workflows/tests/badge.svg)](https://github.com/Fatal1ty/mashumaro/actions)
[![Coverage status](https://codecov.io/github/Fatal1ty/mashumaro/branch/master/graph/badge.svg?token=6hKznmMrWD)](https://codecov.io/github/Fatal1ty/mashumaro)
[![Latest Version](https://img.shields.io/pypi/v/mashumaro.svg)](https://pypi.org/project/mashumaro/)
[![Python Version](https://img.shields.io/pypi/pyversions/mashumaro.svg)](https://pypi.org/project/mashumaro/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

[Documentation](https://mashumaro.io/#/docs/getting-started) ·
[Benchmarks](#performance) ·
[Who uses mashumaro?](#used-across-the-python-ecosystem) ·
[Releases](https://github.com/Fatal1ty/mashumaro/releases)

</div>

## Why mashumaro?

- **Standard Python first.** Keep ordinary dataclasses, collections, and type
  annotations; add a lightweight mixin only when you want methods on a model.
- **Fast by design.** Mashumaro generates conversion code for the exact type
  shape instead of repeatedly inspecting it at runtime.
- **Broad typing support.** Generics, unions, `Annotated`, `Literal`,
  `TypedDict`, `NamedTuple`, recursive models, and much more work recursively.
- **Two simple APIs.** Add methods to a dataclass with a mixin, or create a
  reusable codec for any supported root type such as `list[Event]`.
- **Batteries included.** Convert to dictionaries, JSON, orjson, YAML, TOML,
  and MessagePack, and generate JSON Schema when you need it.

Mashumaro focuses on typed data conversion and serialization. It deliberately
does not try to be a business-rule validation framework or replace your model
layer.

## Used across the Python ecosystem

Mashumaro is used by projects of all kinds, both directly and through other packages. Explore a selection from both groups below.

<p align="center"><strong>Featured projects using mashumaro directly</strong></p>

<!-- github-dependents:featured-direct-dependents-with-logo-start -->
<p align="center">
  <a href="https://github.com/music-assistant/server" title="Music Assistant — direct dependency recorded in pyproject.toml"><img src="https://avatars.githubusercontent.com/u/71128003?s=96&amp;v=4" width="58" height="58" alt="Music Assistant"></a>&nbsp;&nbsp;
  <a href="https://github.com/apple-aiml-research/ml-simplefold" title="SimpleFold — direct dependency recorded in pyproject.toml"><img src="https://avatars.githubusercontent.com/u/321491504?s=96&amp;v=4" width="58" height="58" alt="SimpleFold"></a>&nbsp;&nbsp;
  <a href="https://github.com/flyteorg/flytekit" title="Flytekit — declared runtime dependency"><img src="https://avatars.githubusercontent.com/u/35380635?s=96&amp;v=4" width="58" height="58" alt="Flytekit"></a>&nbsp;&nbsp;
  <a href="https://github.com/recursionpharma/nesso" title="Nesso — direct dependency recorded in pyproject.toml"><img src="https://avatars.githubusercontent.com/u/9286450?s=96&amp;v=4" width="58" height="58" alt="Nesso"></a>&nbsp;&nbsp;
  <a href="https://github.com/pySmartThings/pysmartthings" title="pySmartThings — declared runtime dependency"><img src="https://avatars.githubusercontent.com/u/198121566?s=96&amp;v=4" width="58" height="58" alt="pySmartThings"></a>&nbsp;&nbsp;
  <a href="https://github.com/anchore/vunnel" title="Vunnel — declared runtime dependency"><img src="https://avatars.githubusercontent.com/u/16208487?s=96&amp;v=4" width="58" height="58" alt="Vunnel"></a>&nbsp;&nbsp;
  <a href="https://github.com/esphome/device-builder" title="ESPHome Device Builder — declared runtime dependency"><img src="https://avatars.githubusercontent.com/u/45919759?s=96&amp;v=4" width="58" height="58" alt="ESPHome Device Builder"></a>&nbsp;&nbsp;
  <a href="https://github.com/skodaconnect/myskoda" title="MySkoda — declared runtime dependency"><img src="https://avatars.githubusercontent.com/u/128472441?s=96&amp;v=4" width="58" height="58" alt="MySkoda"></a>&nbsp;&nbsp;
  <a href="https://github.com/dbt-labs/dbt-common" title="dbt-common — declared runtime dependency"><img src="https://avatars.githubusercontent.com/u/18339788?s=96&amp;v=4" width="58" height="58" alt="dbt-common"></a>&nbsp;&nbsp;
  <a href="https://github.com/homewizard/python-homewizard-energy" title="HomeWizard Energy — declared runtime dependency"><img src="https://avatars.githubusercontent.com/u/1442744?s=96&amp;v=4" width="58" height="58" alt="HomeWizard Energy"></a>&nbsp;&nbsp;
  <a href="https://github.com/TrueConf/python-trueconf-bot" title="TrueConf Bot — declared runtime dependency"><img src="https://avatars.githubusercontent.com/u/20208639?s=96&amp;v=4" width="58" height="58" alt="TrueConf Bot"></a>&nbsp;&nbsp;
  <a href="https://github.com/ylab-hi/pxblat" title="pxblat — declared runtime dependency"><img src="https://avatars.githubusercontent.com/u/44730433?s=96&amp;v=4" width="58" height="58" alt="pxblat"></a>
</p>

<p align="center"><sub>Music Assistant · SimpleFold · Flytekit · Nesso · pySmartThings · Vunnel · ESPHome Device Builder · MySkoda · dbt-common · HomeWizard Energy · TrueConf Bot · pxblat</sub></p>
<!-- github-dependents:featured-direct-dependents-with-logo-end -->

<!-- github-dependents:featured-direct-dependent-groups-start -->
<p align="center">
  <strong>Data and developer tools</strong><br>
  <a href="https://github.com/MatsMoll/aligned">Aligned</a> ·
  <a href="https://github.com/dbt-labs/dbt-autofix">dbt-autofix</a> ·
  <a href="https://github.com/flyteorg/flyte-sdk">Flyte SDK</a>
</p>

<p align="center">
  <strong>Science and machine learning</strong><br>
  <a href="https://github.com/kgnlp/allophant">Allophant</a> ·
  <a href="https://github.com/jwohlwend/boltz">Boltz</a> ·
  <a href="https://github.com/DeepFoldProtein/patchr">Patchr</a>
</p>

<p align="center">
  <strong>Devices and web APIs</strong><br>
  <a href="https://github.com/miaucl/bring-api">Bring API</a> ·
  <a href="https://github.com/frenck/python-open-meteo">Open-Meteo</a> ·
  <a href="https://github.com/zweckj/pylamarzocco">pylamarzocco</a> ·
  <a href="https://github.com/mikey0000/PyMammotion">PyMammotion</a> ·
  <a href="https://github.com/python-kasa/python-kasa">python-kasa</a> ·
  <a href="https://github.com/webdjoe/pyvesync">pyvesync</a> ·
  <a href="https://github.com/isaackogan/TikTokLive">TikTokLive</a>
</p>
<!-- github-dependents:featured-direct-dependent-groups-end -->

<!-- github-dependents:more-direct-dependents-start -->
<p align="center"><sub>and <strong>about 100</strong> more projects</sub></p>
<!-- github-dependents:more-direct-dependents-end -->

<p align="center"><strong>Featured projects using mashumaro indirectly</strong></p>

<!-- github-dependents:featured-indirect-dependent-groups-start -->
<p align="center">
  <a href="https://github.com/PrefectHQ/prefect" title="Prefect — transitive dependency-graph relationship"><img src="https://avatars.githubusercontent.com/u/39270919?s=96&amp;v=4" width="58" height="58" alt="Prefect"></a>&nbsp;&nbsp;
  <a href="https://github.com/dlt-hub/dlt" title="dlt — transitive dependency-graph relationship"><img src="https://avatars.githubusercontent.com/u/89419010?s=96&amp;v=4" width="58" height="58" alt="dlt"></a>&nbsp;&nbsp;
  <a href="https://github.com/duneanalytics/spellbook" title="Dune Spellbook — transitive dependency-graph relationship"><img src="https://avatars.githubusercontent.com/u/43092013?s=96&amp;v=4" width="58" height="58" alt="Dune Spellbook"></a>&nbsp;&nbsp;
  <a href="https://github.com/quarylabs/sqruff" title="sqruff — transitive dependency-graph relationship"><img src="https://avatars.githubusercontent.com/u/150465085?s=96&amp;v=4" width="58" height="58" alt="sqruff"></a>&nbsp;&nbsp;
  <a href="https://github.com/zigpy/zha-device-handlers" title="ZHA Device Handlers — transitive dependency-graph relationship"><img src="https://avatars.githubusercontent.com/u/30303551?s=96&amp;v=4" width="58" height="58" alt="ZHA Device Handlers"></a>&nbsp;&nbsp;
  <a href="https://github.com/nordquant/complete-dbt-bootcamp-zero-to-hero" title="Complete dbt Bootcamp — transitive dependency-graph relationship"><img src="https://avatars.githubusercontent.com/u/102964348?s=96&amp;v=4" width="58" height="58" alt="Complete dbt Bootcamp"></a>&nbsp;&nbsp;
  <a href="https://github.com/dbt-labs/dbt-mcp" title="dbt MCP — transitive dependency-graph relationship"><img src="https://avatars.githubusercontent.com/u/18339788?s=96&amp;v=4" width="58" height="58" alt="dbt MCP"></a>&nbsp;&nbsp;
  <a href="https://github.com/DataRecce/recce" title="Recce — transitive dependency-graph relationship"><img src="https://avatars.githubusercontent.com/u/152131563?s=96&amp;v=4" width="58" height="58" alt="Recce"></a>&nbsp;&nbsp;
  <a href="https://github.com/dagster-io/dagster-open-platform" title="Dagster Open Platform — transitive dependency-graph relationship"><img src="https://avatars.githubusercontent.com/u/40032576?s=96&amp;v=4" width="58" height="58" alt="Dagster Open Platform"></a>&nbsp;&nbsp;
  <a href="https://github.com/databrickslabs/dqx" title="Databricks DQX — transitive dependency-graph relationship"><img src="https://avatars.githubusercontent.com/u/49501376?s=96&amp;v=4" width="58" height="58" alt="Databricks DQX"></a>&nbsp;&nbsp;
  <a href="https://github.com/dbt-msft/dbt-sqlserver" title="dbt-sqlserver — transitive dependency-graph relationship"><img src="https://avatars.githubusercontent.com/u/73860967?s=96&amp;v=4" width="58" height="58" alt="dbt-sqlserver"></a>&nbsp;&nbsp;
  <a href="https://github.com/microsoft/dbt-fabric" title="dbt-fabric — transitive dependency-graph relationship"><img src="https://avatars.githubusercontent.com/u/6154722?s=96&amp;v=4" width="58" height="58" alt="dbt-fabric"></a>
</p>

<p align="center"><sub>Prefect · dlt · Dune Spellbook · sqruff · ZHA Device Handlers · Complete dbt Bootcamp · dbt MCP · Recce · Dagster Open Platform · Databricks DQX · dbt-sqlserver · dbt-fabric</sub></p>

<p align="center">
  <strong>Data and dbt tooling</strong><br>
  <a href="https://github.com/tomasfarias/airflow-dbt-python">airflow-dbt-python</a> ·
  <a href="https://github.com/gouline/dbt-metabase">dbt-metabase</a> ·
  <a href="https://github.com/z3z1ma/dbt-osmosis">dbt-osmosis</a> ·
  <a href="https://github.com/PicnicSupermarket/dbt-score">dbt-score</a> ·
  <a href="https://github.com/datnguye/dbterd">dbterd</a>
</p>

<p align="center">
  <strong>Connected-device integrations</strong><br>
  <a href="https://github.com/alandtse/alexa_media_player">Alexa Media Player</a> ·
  <a href="https://github.com/KartoffelToby/better_thermostat">Better Thermostat</a> ·
  <a href="https://github.com/dvd-dev/hilo">Hilo</a> ·
  <a href="https://github.com/skodaconnect/homeassistant-myskoda">Home Assistant MySkoda</a> ·
  <a href="https://github.com/wuwentao/midea_ac_lan">Midea AC LAN</a> ·
  <a href="https://github.com/bramstroker/homeassistant-powercalc">Powercalc</a> ·
  <a href="https://github.com/frenck/spook">Spook</a> ·
  <a href="https://github.com/pytoyoda/ha_toyota">Toyota Connected Services</a>
</p>
<!-- github-dependents:featured-indirect-dependent-groups-end -->

<!-- github-dependents:more-indirect-dependents-start -->
<p align="center"><sub>and <strong>about 500</strong> more projects</sub></p>
<!-- github-dependents:more-indirect-dependents-end -->

<details>
<summary>Selection and verification</summary>

<p><!-- github-dependents:snapshot-date-start -->The September 21, 2026<!-- github-dependents:snapshot-date-end -->
snapshot paginated all
<!-- github-dependents:dep-graph-pages-start -->117<!-- github-dependents:dep-graph-pages-end -->
pages of the repository view of the
<a href="https://github.com/Fatal1ty/mashumaro/network/dependents">GitHub dependency graph</a>
and cross-referenced its package view. It found
<!-- github-dependents:starred-repos-start -->924<!-- github-dependents:starred-repos-end -->
repositories with at least two stars; after excluding
<!-- github-dependents:excluded-starred-repo-forks-start -->36<!-- github-dependents:excluded-starred-repo-forks-end -->
forks,
<!-- github-dependents:remained-starred-repos-start -->888<!-- github-dependents:remained-starred-repos-end -->
remained. After verification,
<!-- github-dependents:conventional-direct-dependencies-start -->125<!-- github-dependents:conventional-direct-dependencies-end -->
had direct evidence in conventional dependency files and
<!-- github-dependents:unusual-direct-dependencies-start -->11<!-- github-dependents:unusual-direct-dependencies-end -->
more in unusual locations. Another
<!-- github-dependents:transitive-dependencies-start -->495<!-- github-dependents:transitive-dependencies-end -->
had only effective transitive evidence, while
<!-- github-dependents:unresolved-dependencies-start -->257<!-- github-dependents:unresolved-dependencies-end -->
could not be resolved.</p>

Only exactly named dependency files in the repository root or directly under
`src/` are treated as conventional locations. GitHub's relationship is accepted
for declaration files such as `pyproject.toml`, `setup.py`, `setup.cfg`, and
`requirements.in`. Lockfiles and requirements snapshots that GitHub labels
`direct` receive an additional content check. If another locked package depends
on mashumaro and there is no edge from the local project, the relationship is
reclassified as transitive. A `requirements.txt` entry is direct only when its
own `# via` provenance points to an input declaration; freeze-style snapshots
without per-entry provenance remain unresolved unless other evidence is
conclusive. When a conventional dependency file has no recognizable GitHub
relationship label, its contents are checked directly; an explicit declaration
can still confirm direct use, while unreadable or ambiguous evidence fails
closed as unresolved.

When GitHub's package view identifies a published package, its PyPI
`requires_dist` metadata provides a second directness check. An explicit
mashumaro requirement confirms direct use; a conclusive absence rejects the
GitHub-direct result. Network and metadata failures are treated as
inconclusive. Every project shown in the indirect usage sample therefore has
only effective `transitive` relationships; unresolved repositories are counted
but not featured.

For the gallery, each candidate was reviewed in context. A project was kept
when mashumaro belongs to its maintained application, library, or clearly
named product component. Repositories where the match came only from a demo,
benchmark, test fixture, vendored copy, or generated dependency set were left
out. This avoids presenting incidental development environments as product
adoption.

Images are limited to organization marks from the reviewed repository data;
projects under personal accounts are listed by name instead. Dependency data,
repository activity, and ownership can change between snapshots. Logos belong
to their respective projects, and inclusion does not imply endorsement.

</details>

## Installation

```bash
pip install mashumaro
```

The current release supports Python 3.10–3.14. Install optional formats only
when you need them:

```bash
pip install "mashumaro[orjson,yaml,toml,msgpack]"
```

See [Migration and Compatibility](https://mashumaro.io/#/docs/migration-and-compatibility)
for the last releases supporting older Python versions.

## Quick start

### Add serialization methods to a dataclass

```python
from dataclasses import dataclass
from datetime import datetime

from mashumaro.mixins.json import DataClassJSONMixin


@dataclass
class Event(DataClassJSONMixin):
    name: str
    starts_at: datetime
    speakers: list[str]


event = Event(
    name="PyCon",
    starts_at=datetime(2026, 5, 13, 9, 0),
    speakers=["Alice", "Bob"],
)

payload = event.to_json()
restored = Event.from_json(payload)

assert restored == event
```

Nested dataclasses remain plain dataclasses; only the root model needs the
mixin. Format-specific mixins for orjson, YAML, TOML, and MessagePack expose
the same style of API.

### Build a codec for any supported type shape

```python
from mashumaro.codecs.json import JSONDecoder, JSONEncoder

encoder = JSONEncoder(list[Event])
decoder = JSONDecoder(list[Event])

payload = encoder.encode([event])
restored = decoder.decode(payload)

assert restored == [event]
```

Construct codecs once and reuse them when performance matters. A codec root
can be a dataclass, collection, `TypedDict`, union, scalar, or another
supported type shape.

## Performance

Mashumaro generates specialized conversion functions once, then reuses them
without repeatedly walking fields and annotations. The repository benchmark
uses [pyperf](https://github.com/psf/pyperf) and a nested GitHub Issue model.

The results below were recorded on macOS 15.1, an Apple M3 Max, and Python
3.13.0. Lower is better; the charts use a logarithmic scale.

<picture>
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Fatal1ty/mashumaro/refs/heads/master/benchmark/charts/load_light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Fatal1ty/mashumaro/refs/heads/master/benchmark/charts/load_dark.svg">
  <img alt="Deserialization benchmark" src="https://raw.githubusercontent.com/Fatal1ty/mashumaro/refs/heads/master/benchmark/charts/load_light.svg" width="604">
</picture>

<picture>
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Fatal1ty/mashumaro/refs/heads/master/benchmark/charts/dump_light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Fatal1ty/mashumaro/refs/heads/master/benchmark/charts/dump_dark.svg">
  <img alt="Serialization benchmark" src="https://raw.githubusercontent.com/Fatal1ty/mashumaro/refs/heads/master/benchmark/charts/dump_light.svg" width="604">
</picture>

Benchmarks are workload- and configuration-dependent. Compare equivalent
validation, conversion, and output semantics before drawing conclusions. See
the [performance guide](https://mashumaro.io/#/docs/performance) for methodology
and run `./benchmark/run.sh` to reproduce the benchmark locally.

## What is supported?

| Area | Highlights |
|---|---|
| Types | Dataclasses, collections, tuples, mappings, enums, modern typing constructs, generics, date/time types, UUIDs, decimals, paths, IP addresses, and user-defined types |
| Formats | Dictionary/basic form, JSON, orjson, YAML, TOML, and MessagePack |
| Customization | Field aliases, serialization strategies, dialects, hooks, discriminators, omission rules, and configuration inheritance |
| Schemas | JSON Schema Draft 2020-12 and OpenAPI 3.1 |

The complete behavior and format-specific representations are documented in
[Supported Types](https://mashumaro.io/#/docs/supported-types) and
[Supported Formats](https://mashumaro.io/#/docs/supported-formats).

## Documentation

- [Getting Started](https://mashumaro.io/#/docs/getting-started)
- [Field Options](https://mashumaro.io/#/docs/field-options)
- [Config Options](https://mashumaro.io/#/docs/config-options)
- [Custom Serialization Strategies](https://mashumaro.io/#/docs/serializationstrategy)
- [Discriminated Unions](https://mashumaro.io/#/docs/discriminator)
- [JSON Schema](https://mashumaro.io/#/docs/json-schema)
- [Performance Guide](https://mashumaro.io/#/docs/performance)
- [Errors and Troubleshooting](https://mashumaro.io/#/docs/errors-and-troubleshooting)
- [API Reference](https://mashumaro.io/#/docs/api-reference)

## Contributing

Bug reports and pull requests are welcome. Please read the
[contributing guide](https://github.com/Fatal1ty/mashumaro/blob/master/.github/CONTRIBUTING.md)
and report security issues according to the
[security policy](https://github.com/Fatal1ty/mashumaro/security/policy).

Mashumaro is distributed under the
[Apache License 2.0](https://github.com/Fatal1ty/mashumaro/blob/master/LICENSE).
