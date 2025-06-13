<div align="center">

<img alt="logo" width="175" src="https://raw.githubusercontent.com/Fatal1ty/mashumaro/ac2f924591d488dbd9a776a6b1ae7dede2d8c73e/img/logo.svg">

###### Fast and well tested serialization library

[![Build Status](https://github.com/Fatal1ty/mashumaro/workflows/tests/badge.svg)](https://github.com/Fatal1ty/mashumaro/actions)
[![Coverage Status](https://coveralls.io/repos/github/Fatal1ty/mashumaro/badge.svg?branch=master)](https://coveralls.io/github/Fatal1ty/mashumaro?branch=master)
[![Latest Version](https://img.shields.io/pypi/v/mashumaro.svg)](https://pypi.python.org/pypi/mashumaro)
[![Python Version](https://img.shields.io/pypi/pyversions/mashumaro.svg)](https://pypi.python.org/pypi/mashumaro)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
</div>

In Python, you often need to dump and load objects based on the schema you
have. It can be a dataclass model, a list of third-party generic classes or
whatever. Mashumaro not only lets you save and load things in different ways,
but it also does it _super quick_.

**Key features**
* 🚀 One of the fastest libraries
* ☝️ Mature and time-tested
* 👶 Easy to use out of the box
* ⚙️ Highly customizable
* 🎉 Built-in support for JSON, YAML, TOML, MessagePack
* 📦 Built-in support for almost all Python types including typing-extensions
* 📝 JSON Schema generation

Table of contents
-------------------------------------------------------------------------------
* [Table of contents](#table-of-contents)
* [Introduction](#introduction)
* [Installation](#installation)
* [Changelog](#changelog)
* [Supported data types](#supported-data-types)
* [Usage example](#usage-example)
* [How does it work?](#how-does-it-work)
* [Benchmark](#benchmark)
* [Supported serialization formats](#supported-serialization-formats)
    * [Basic form](#basic-form)
    * [JSON](#json)
        * [json library](#json-library)
        * [orjson library](#orjson-library)
    * [YAML](#yaml)
    * [TOML](#toml)
    * [MessagePack](#messagepack)
* [Customization](#customization)
    * [SerializableType interface](#serializabletype-interface)
        * [User-defined types](#user-defined-types)
        * [User-defined generic types](#user-defined-generic-types)
    * [SerializationStrategy](#serializationstrategy)
        * [Third-party types](#third-party-types)
        * [Third-party generic types](#third-party-generic-types)
    * [Field options](#field-options)
        * [`serialize` option](#serialize-option)
        * [`deserialize` option](#deserialize-option)
        * [`serialization_strategy` option](#serialization_strategy-option)
        * [`alias` option](#alias-option)
    * [Config options](#config-options)
        * [`debug` config option](#debug-config-option)
        * [`code_generation_options` config option](#code_generation_options-config-option)
        * [`serialization_strategy` config option](#serialization_strategy-config-option)
        * [`aliases` config option](#aliases-config-option)
        * [`serialize_by_alias` config option](#serialize_by_alias-config-option)
        * [`allow_deserialization_not_by_alias` config option](#allow_deserialization_not_by_alias-config-option)
        * [`omit_none` config option](#omit_none-config-option)
        * [`omit_default` config option](#omit_default-config-option)
        * [`namedtuple_as_dict` config option](#namedtuple_as_dict-config-option)
        * [`allow_postponed_evaluation` config option](#allow_postponed_evaluation-config-option)
        * [`dialect` config option](#dialect-config-option)
        * [`orjson_options` config option](#orjson_options-config-option)
        * [`discriminator` config option](#discriminator-config-option)
        * [`lazy_compilation` config option](#lazy_compilation-config-option)
        * [`sort_keys` config option](#sort_keys-config-option)
        * [`forbid_extra_keys` config option](#forbid_extra_keys-config-option)
    * [Passing field values as is](#passing-field-values-as-is)
    * [Extending existing types](#extending-existing-types)
    * [Field aliases](#field-aliases)
    * [Dialects](#dialects)
        * [`serialization_strategy` dialect option](#serialization_strategy-dialect-option)
        * [`serialize_by_alias` dialect option](#serialize_by_alias-dialect-option)
        * [`omit_none` dialect option](#omit_none-dialect-option)
        * [`omit_default` dialect option](#omit_default-dialect-option)
        * [`namedtuple_as_dict` dialect option](#namedtuple_as_dict-dialect-option)
        * [`no_copy_collections` dialect option](#no_copy_collections-dialect-option)
        * [Changing the default dialect](#changing-the-default-dialect)
    * [Discriminator](#discriminator)
        * [Subclasses distinguishable by a field](#subclasses-distinguishable-by-a-field)
        * [Subclasses without a common field](#subclasses-without-a-common-field)
        * [Class level discriminator](#class-level-discriminator)
        * [Working with union of classes](#working-with-union-of-classes)
        * [Using a custom variant tagger function](#using-a-custom-variant-tagger-function)
    * [Code generation options](#code-generation-options)
        * [Add `omit_none` keyword argument](#add-omit_none-keyword-argument)
        * [Add `by_alias` keyword argument](#add-by_alias-keyword-argument)
        * [Add `dialect` keyword argument](#add-dialect-keyword-argument)
        * [Add `context` keyword argument](#add-context-keyword-argument)
    * [Generic dataclasses](#generic-dataclasses)
        * [Generic dataclass inheritance](#generic-dataclass-inheritance)
        * [Generic dataclass in a field type](#generic-dataclass-in-a-field-type)
    * [GenericSerializableType interface](#genericserializabletype-interface)
    * [Serialization hooks](#serialization-hooks)
        * [Before deserialization](#before-deserialization)
        * [After deserialization](#after-deserialization)
        * [Before serialization](#before-serialization)
        * [After serialization](#after-serialization)
* [JSON Schema](#json-schema)
    * [Building JSON Schema](#building-json-schema)
    * [JSON Schema constraints](#json-schema-constraints)
    * [JSON Schema plugins](#json-schema-plugins)
    * [Extending JSON Schema](#extending-json-schema)
    * [JSON Schema and custom serialization methods](#json-schema-and-custom-serialization-methods)

Introduction
-------------------------------------------------------------------------------

This library provides two fundamentally different approaches to converting
your data to and from various formats. Each of them is useful in different
situations:

* Codecs
* Mixins

Codecs are represented by a set of decoder / encoder classes and
decode / encode functions for each supported format. You can use them
to convert data of any python built-in and third-party type to JSON, YAML,
TOML, MessagePack or a basic form accepted by other serialization formats.
For example, you can convert a list of datetime objects to JSON array
containing string-represented datetimes and vice versa.

Mixins are primarily for dataclass models. They are represented by mixin
classes that add methods for converting to and from JSON, YAML, TOML,
MessagePack or a basic form accepted by other serialization formats.
If you have a root dataclass model, then it will be the easiest way to make it
serializable. All you have to do is inherit a particular mixin class.

In addition to serialization functionality, this library also provides JSON
Schema builder that can be used in places where interoperability matters.

Installation
-------------------------------------------------------------------------------

Use pip to install:
```shell
$ pip install mashumaro
```

The current version of `mashumaro` supports Python versions 3.9 — 3.13.


It's not recommended to use any version of Python that has reached its
[end of life](https://devguide.python.org/versions/) and is no longer receiving
security updates or bug fixes from the Python development team.
For convenience, there is a table below that outlines the
last version of `mashumaro` that can be installed on unmaintained versions
of Python.

| Python Version | Last Version of mashumaro                                          | Python EOL |
|----------------|--------------------------------------------------------------------|------------|
| 3.8            | [3.14](https://github.com/Fatal1ty/mashumaro/releases/tag/v3.14)   | 2024-10-07 |
| 3.7            | [3.9.1](https://github.com/Fatal1ty/mashumaro/releases/tag/v3.9.1) | 2023-06-27 |
| 3.6            | [3.1.1](https://github.com/Fatal1ty/mashumaro/releases/tag/v3.1.1) | 2021-12-23 |


Changelog
-------------------------------------------------------------------------------

This project follows the principles of [Semantic Versioning](https://semver.org).
Changelog is available on [GitHub Releases page](https://github.com/Fatal1ty/mashumaro/releases).

Supported data types
-------------------------------------------------------------------------------

There is support for generic types from the standard [`typing`](https://docs.python.org/3/library/typing.html) module:
* [`List`](https://docs.python.org/3/library/typing.html#typing.List)
* [`Tuple`](https://docs.python.org/3/library/typing.html#typing.Tuple)
* [`NamedTuple`](https://docs.python.org/3/library/typing.html#typing.NamedTuple)
* [`Set`](https://docs.python.org/3/library/typing.html#typing.Set)
* [`FrozenSet`](https://docs.python.org/3/library/typing.html#typing.FrozenSet)
* [`Deque`](https://docs.python.org/3/library/typing.html#typing.Deque)
* [`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)
* [`OrderedDict`](https://docs.python.org/3/library/typing.html#typing.OrderedDict)
* [`DefaultDict`](https://docs.python.org/3/library/typing.html#typing.DefaultDict)
* [`TypedDict`](https://docs.python.org/3/library/typing.html#typing.TypedDict)
* [`Mapping`](https://docs.python.org/3/library/typing.html#typing.Mapping)
* [`MutableMapping`](https://docs.python.org/3/library/typing.html#typing.MutableMapping)
* [`Counter`](https://docs.python.org/3/library/typing.html#typing.Counter)
* [`ChainMap`](https://docs.python.org/3/library/typing.html#typing.ChainMap)
* [`Sequence`](https://docs.python.org/3/library/typing.html#typing.Sequence)

for standard generic types on [PEP 585](https://www.python.org/dev/peps/pep-0585/) compatible Python (3.9+):
* [`list`](https://docs.python.org/3/library/stdtypes.html#list)
* [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple)
* [`namedtuple`](https://docs.python.org/3/library/collections.html#collections.namedtuple)
* [`set`](https://docs.python.org/3/library/stdtypes.html#set)
* [`frozenset`](https://docs.python.org/3/library/stdtypes.html#frozenset)
* [`collections.abc.Set`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Set)
* [`collections.abc.MutableSet`](https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableSet)
* [`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque)
* [`dict`](https://docs.python.org/3/library/stdtypes.html#dict)
* [`collections.OrderedDict`](https://docs.python.org/3/library/collections.html#collections.OrderedDict)
* [`collections.defaultdict`](https://docs.python.org/3/library/collections.html#collections.defaultdict)
* [`collections.abc.Mapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Mapping)
* [`collections.abc.MutableMapping`](https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableMapping)
* [`collections.Counter`](https://docs.python.org/3/library/collections.html#collections.Counter)
* [`collections.ChainMap`](https://docs.python.org/3/library/collections.html#collections.ChainMap)
* [`collections.abc.Sequence`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Sequence)
* [`collections.abc.MutableSequence`](https://docs.python.org/3/library/collections.abc.html#collections.abc.MutableSequence)

for special primitives from the [`typing`](https://docs.python.org/3/library/typing.html) module:
* [`Any`](https://docs.python.org/3/library/typing.html#typing.Any)
* [`Optional`](https://docs.python.org/3/library/typing.html#typing.Optional)
* [`Union`](https://docs.python.org/3/library/typing.html#typing.Union)
* [`TypeVar`](https://docs.python.org/3/library/typing.html#typing.TypeVar)
* [`TypeVarTuple`](https://docs.python.org/3/library/typing.html#typing.TypeVarTuple)
* [`NewType`](https://docs.python.org/3/library/typing.html#newtype)
* [`Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated)
* [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal)
* [`LiteralString`](https://docs.python.org/3/library/typing.html#typing.LiteralString)
* [`Final`](https://docs.python.org/3/library/typing.html#typing.Final)
* [`Self`](https://docs.python.org/3/library/typing.html#typing.Self)
* [`Unpack`](https://docs.python.org/3/library/typing.html#typing.Unpack)
* [`ReadOnly`](https://docs.python.org/3/library/typing.html#typing.ReadOnly)

for standard interpreter types from [`types`](https://docs.python.org/3/library/types.html#standard-interpreter-types) module:
* [`NoneType`](https://docs.python.org/3/library/types.html#types.NoneType)
* [`UnionType`](https://docs.python.org/3/library/types.html#types.UnionType)
* [`MappingProxyType`](https://docs.python.org/3/library/types.html#types.MappingProxyType)

for enumerations based on classes from the standard [`enum`](https://docs.python.org/3/library/enum.html) module:
* [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)
* [`IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum)
* [`StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)
* [`Flag`](https://docs.python.org/3/library/enum.html#enum.Flag)
* [`IntFlag`](https://docs.python.org/3/library/enum.html#enum.IntFlag)

for common built-in types:
* [`int`](https://docs.python.org/3/library/functions.html#int)
* [`float`](https://docs.python.org/3/library/functions.html#float)
* [`bool`](https://docs.python.org/3/library/stdtypes.html#bltin-boolean-values)
* [`str`](https://docs.python.org/3/library/stdtypes.html#str)
* [`bytes`](https://docs.python.org/3/library/stdtypes.html#bytes)
* [`bytearray`](https://docs.python.org/3/library/stdtypes.html#bytearray)

for built-in datetime oriented types (see [more](#deserialize-option) details):
* [`datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime)
* [`date`](https://docs.python.org/3/library/datetime.html#datetime.date)
* [`time`](https://docs.python.org/3/library/datetime.html#datetime.time)
* [`timedelta`](https://docs.python.org/3/library/datetime.html#datetime.timedelta)
* [`timezone`](https://docs.python.org/3/library/datetime.html#datetime.timezone)
* [`ZoneInfo`](https://docs.python.org/3/library/zoneinfo.html#zoneinfo.ZoneInfo)

for pathlike types:
* [`PurePath`](https://docs.python.org/3/library/pathlib.html#pathlib.PurePath)
* [`Path`](https://docs.python.org/3/library/pathlib.html#pathlib.Path)
* [`PurePosixPath`](https://docs.python.org/3/library/pathlib.html#pathlib.PurePosixPath)
* [`PosixPath`](https://docs.python.org/3/library/pathlib.html#pathlib.PosixPath)
* [`PureWindowsPath`](https://docs.python.org/3/library/pathlib.html#pathlib.PureWindowsPath)
* [`WindowsPath`](https://docs.python.org/3/library/pathlib.html#pathlib.WindowsPath)
* [`os.PathLike`](https://docs.python.org/3/library/os.html#os.PathLike)

for other less popular built-in types:
* [`uuid.UUID`](https://docs.python.org/3/library/uuid.html#uuid.UUID)
* [`decimal.Decimal`](https://docs.python.org/3/library/decimal.html#decimal.Decimal)
* [`fractions.Fraction`](https://docs.python.org/3/library/fractions.html#fractions.Fraction)
* [`ipaddress.IPv4Address`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Address)
* [`ipaddress.IPv6Address`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv6Address)
* [`ipaddress.IPv4Network`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Network)
* [`ipaddress.IPv6Network`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv6Network)
* [`ipaddress.IPv4Interface`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv4Interface)
* [`ipaddress.IPv6Interface`](https://docs.python.org/3/library/ipaddress.html#ipaddress.IPv6Interface)
* [`typing.Pattern`](https://docs.python.org/3/library/typing.html#typing.Pattern)
* [`re.Pattern`](https://docs.python.org/3/library/re.html#re.Pattern)

for backported types from [`typing-extensions`](https://github.com/python/typing_extensions):
* [`OrderedDict`](https://docs.python.org/3/library/typing.html#typing.OrderedDict)
* [`TypedDict`](https://docs.python.org/3/library/typing.html#typing.TypedDict)
* [`Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated)
* [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal)
* [`LiteralString`](https://docs.python.org/3/library/typing.html#typing.LiteralString)
* [`Self`](https://docs.python.org/3/library/typing.html#typing.Self)
* [`TypeVarTuple`](https://docs.python.org/3/library/typing.html#typing.TypeVarTuple)
* [`Unpack`](https://docs.python.org/3/library/typing.html#typing.Unpack)
* [`ReadOnly`](https://docs.python.org/3/library/typing.html#typing.ReadOnly)

for arbitrary types:
* [user-defined types](#user-defined-types)
* [third-party types](#third-party-types)
* [user-defined generic types](#user-defined-generic-types)
* [third-party generic types](#third-party-generic-types)

Usage example
-------------------------------------------------------------------------------

Suppose we're developing a financial application and we operate with currencies
and stocks:

```python
from dataclasses import dataclass
from enum import Enum

class Currency(Enum):
    USD = "USD"
    EUR = "EUR"

@dataclass
class CurrencyPosition:
    currency: Currency
    balance: float

@dataclass
class StockPosition:
    ticker: str
    name: str
    balance: int
```

Now we want a dataclass for portfolio that will be serialized to and from JSON.
We inherit `DataClassJSONMixin` that adds this functionality:

```python
from mashumaro.mixins.json import DataClassJSONMixin

...

@dataclass
class Portfolio(DataClassJSONMixin):
    currencies: list[CurrencyPosition]
    stocks: list[StockPosition]
```

Let's create a portfolio instance and check methods `from_json` and `to_json`:

```python
portfolio = Portfolio(
    currencies=[
        CurrencyPosition(Currency.USD, 238.67),
        CurrencyPosition(Currency.EUR, 361.84),
    ],
    stocks=[
        StockPosition("AAPL", "Apple", 10),
        StockPosition("AMZN", "Amazon", 10),
    ]
)

portfolio_json = portfolio.to_json()
assert Portfolio.from_json(portfolio_json) == portfolio
```

If we need to serialize something different from a root dataclass,
we can use codecs. In the following example we create a JSON decoder and encoder
for a list of currencies:

```python
from mashumaro.codecs.json import JSONDecoder, JSONEncoder

...

decoder = JSONDecoder(list[CurrencyPosition])
encoder = JSONEncoder(list[CurrencyPosition])

currencies = [
    CurrencyPosition(Currency.USD, 238.67),
    CurrencyPosition(Currency.EUR, 361.84),
]
currencies_json = encoder.encode(currencies)
assert decoder.decode(currencies_json) == currencies

```

How does it work?
-------------------------------------------------------------------------------

This library works by taking the schema of the data and generating a
specific decoder and encoder for exactly that schema, taking into account the
specifics of serialization format. This is much faster than inspection of
data types on every call of decoding or encoding at runtime.

These specific decoders and encoders are generated by
[codecs and mixins](#supported-serialization-formats):
* When using codecs, these methods are compiled during the creation of the
  decoder or encoder.
* When using serialization
mixins, these methods are compiled during import time (or at runtime in some
cases) and are set as attributes to your dataclasses. To minimize the import
time, you can explicitly enable
[lazy compilation](#lazy_compilation-config-option).

Benchmark
-------------------------------------------------------------------------------

* macOS 15.1 Sequoia
* Apple M3 Max
* 36GB RAM
* Python 3.13.0

Benchmark using [pyperf](https://github.com/psf/pyperf) with GitHub Issue model. Please note that the
following charts use logarithmic scale, as it is convenient for displaying
very large ranges of values.

<picture>
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Fatal1ty/mashumaro/refs/heads/master/benchmark/charts/load_light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Fatal1ty/mashumaro/refs/heads/master/benchmark/charts/load_dark.svg">
  <img src="https://raw.githubusercontent.com/Fatal1ty/mashumaro/refs/heads/master/benchmark/charts/load_light.svg" width="604">
</picture>
<picture>
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Fatal1ty/mashumaro/refs/heads/master/benchmark/charts/dump_light.svg">
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Fatal1ty/mashumaro/refs/heads/master/benchmark/charts/dump_dark.svg">
  <img src="https://raw.githubusercontent.com/Fatal1ty/mashumaro/refs/heads/master/benchmark/charts/dump_light.svg" width="604">
</picture>

> [!NOTE]\
> Benchmark results may vary depending on the specific configuration and
> parameters used for serialization and deserialization. However, we have made
> an attempt to use the available options that can speed up and smooth out the
> differences in how libraries work.

To run benchmark in your environment:
```bash
git clone git@github.com:Fatal1ty/mashumaro.git
cd mashumaro
python3 -m venv env && source env/bin/activate
pip install -e .
pip install -r requirements-dev.txt
./benchmark/run.sh
```

Supported serialization formats
-------------------------------------------------------------------------------

This library has built-in support for multiple popular formats:

* [JSON](https://www.json.org)
* [YAML](https://yaml.org)
* [TOML](https://toml.io)
* [MessagePack](https://msgpack.org)

There are preconfigured codecs and mixin classes. However, you're free
to override some settings if necessary.

> [!IMPORTANT]\
> As for codecs, you are
> offered to choose between convenience and efficiency. When you need to decode
> or encode typed data more than once, it's highly recommended to create
> and reuse a decoder or encoder specifically for that data type. For one-time
> use with default settings it may be convenient to use global functions that
> create a disposable decoder or encoder under the hood. Remember that you
> should not use these convenient global functions more that once for the same
> data type if performance is important to you.

### Basic form

Basic form denotes a python object consisting only of basic data types
supported by most serialization formats. These types are:
[`str`](https://docs.python.org/3/library/stdtypes.html#str),
[`int`](https://docs.python.org/3/library/functions.html#int),
[`float`](https://docs.python.org/3/library/functions.html#float),
[`bool`](https://docs.python.org/3/library/stdtypes.html#bltin-boolean-values),
[`list`](https://docs.python.org/3/library/stdtypes.html#list),
[`dict`](https://docs.python.org/3/library/stdtypes.html#dict).

This is also a starting point you can play with for a comprehensive
transformation of your data.

Efficient decoder and encoder can be used as follows:

```python
from mashumaro.codecs import BasicDecoder, BasicEncoder
# or from mashumaro.codecs.basic import BasicDecoder, BasicEncoder

decoder = BasicDecoder(<shape_type>, ...)
decoder.decode(...)

encoder = BasicEncoder(<shape_type>, ...)
encoder.encode(...)
```

Convenient functions are recommended to be used as follows:
```python
import mashumaro.codecs.basic as basic_codec

basic_codec.decode(..., <shape_type>)
basic_codec.encode(..., <shape_type>)
```

Mixin can be used as follows:
```python
from mashumaro import DataClassDictMixin
# or from mashumaro.mixins.dict import DataClassDictMixin

@dataclass
class MyModel(DataClassDictMixin):
    ...

MyModel.from_dict(...)
MyModel(...).to_dict()
```

> [!TIP]\
> You don't need to inherit `DataClassDictMixin` along with other serialization
> mixins because it's a base class for them.

### JSON

[JSON](https://www.json.org) is a lightweight data-interchange format. You can
choose between standard library
[json](https://docs.python.org/3/library/json.html) for compatibility and
third-party dependency [orjson](https://pypi.org/project/orjson/) for better
performance.

#### json library

Efficient decoder and encoder can be used as follows:
```python
from mashumaro.codecs.json import JSONDecoder, JSONEncoder

decoder = JSONDecoder(<shape_type>, ...)
decoder.decode(...)

encoder = JSONEncoder(<shape_type>, ...)
encoder.encode(...)
```

Convenient functions can be used as follows:
```python
from mashumaro.codecs.json import json_decode, json_encode

json_decode(..., <shape_type>)
json_encode(..., <shape_type>)
```

Convenient function aliases are recommended to be used as follows:
```python
import mashumaro.codecs.json as json_codec

json_codec.decode(...<shape_type>)
json_codec.encode(..., <shape_type>)
```

Mixin can be used as follows:
```python
from mashumaro.mixins.json import DataClassJSONMixin

@dataclass
class MyModel(DataClassJSONMixin):
    ...

MyModel.from_json(...)
MyModel(...).to_json()
```

#### orjson library

In order to use [`orjson`](https://pypi.org/project/orjson/) library, it must
be installed manually or using an extra option for `mashumaro`:

```shell
pip install mashumaro[orjson]
```

The following data types will be handled by
[`orjson`](https://pypi.org/project/orjson/) library by default:
* [`datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime)
* [`date`](https://docs.python.org/3/library/datetime.html#datetime.date)
* [`time`](https://docs.python.org/3/library/datetime.html#datetime.time)
* [`uuid.UUID`](https://docs.python.org/3/library/uuid.html#uuid.UUID)

Efficient decoder and encoder can be used as follows:
```python
from mashumaro.codecs.orjson import ORJSONDecoder, ORJSONEncoder

decoder = ORJSONDecoder(<shape_type>, ...)
decoder.decode(...)

encoder = ORJSONEncoder(<shape_type>, ...)
encoder.encode(...)
```

Convenient functions can be used as follows:
```python
from mashumaro.codecs.orjson import json_decode, json_encode

json_decode(..., <shape_type>)
json_encode(..., <shape_type>)
```

Convenient function aliases are recommended to be used as follows:
```python
import mashumaro.codecs.orjson as json_codec

json_codec.decode(...<shape_type>)
json_codec.encode(..., <shape_type>)
```

Mixin can be used as follows:
```python
from mashumaro.mixins.orjson import DataClassORJSONMixin

@dataclass
class MyModel(DataClassORJSONMixin):
    ...

MyModel.from_json(...)
MyModel(...).to_json()
MyModel(...).to_jsonb()
```

### YAML

[YAML](https://yaml.org) is a human-friendly data serialization language for
all programming languages. In order to use this format, the
[`pyyaml`](https://pypi.org/project/PyYAML/) package must be installed.
You can install it manually or using an extra option for `mashumaro`:

```shell
pip install mashumaro[yaml]
```

Efficient decoder and encoder can be used as follows:
```python
from mashumaro.codecs.yaml import YAMLDecoder, YAMLEncoder

decoder = YAMLDecoder(<shape_type>, ...)
decoder.decode(...)

encoder = YAMLEncoder(<shape_type>, ...)
encoder.encode(...)
```

Convenient functions can be used as follows:
```python
from mashumaro.codecs.yaml import yaml_decode, yaml_encode

yaml_decode(..., <shape_type>)
yaml_encode(..., <shape_type>)
```

Convenient function aliases are recommended to be used as follows:
```python
import mashumaro.codecs.yaml as yaml_codec

yaml_codec.decode(...<shape_type>)
yaml_codec.encode(..., <shape_type>)
```

Mixin can be used as follows:
```python
from mashumaro.mixins.yaml import DataClassYAMLMixin

@dataclass
class MyModel(DataClassYAMLMixin):
    ...

MyModel.from_yaml(...)
MyModel(...).to_yaml()
```

### TOML

[TOML](https://toml.io) is config file format for humans.
In order to use this format, the [`tomli`](https://pypi.org/project/tomli/) and
[`tomli-w`](https://pypi.org/project/tomli-w/) packages must be installed.
In Python 3.11+, `tomli` is included as
[`tomlib`](https://docs.python.org/3/library/tomllib.html) standard library
module and is used for this format. You can install the missing packages
manually or using an extra option
for `mashumaro`:

```shell
pip install mashumaro[toml]
```

The following data types will be handled by
[`tomli`](https://pypi.org/project/tomli/)/
[`tomli-w`](https://pypi.org/project/tomli-w/) library by default:
* [`datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime)
* [`date`](https://docs.python.org/3/library/datetime.html#datetime.date)
* [`time`](https://docs.python.org/3/library/datetime.html#datetime.time)

Fields with value `None` will be omitted on serialization because TOML
doesn't support null values.

Efficient decoder and encoder can be used as follows:
```python
from mashumaro.codecs.toml import TOMLDecoder, TOMLEncoder

decoder = TOMLDecoder(<shape_type>, ...)
decoder.decode(...)

encoder = TOMLEncoder(<shape_type>, ...)
encoder.encode(...)
```

Convenient functions can be used as follows:
```python
from mashumaro.codecs.toml import toml_decode, toml_encode

toml_decode(..., <shape_type>)
toml_encode(..., <shape_type>)
```

Convenient function aliases are recommended to be used as follows:
```python
import mashumaro.codecs.toml as toml_codec

toml_codec.decode(...<shape_type>)
toml_codec.encode(..., <shape_type>)
```

Mixin can be used as follows:
```python
from mashumaro.mixins.toml import DataClassTOMLMixin

@dataclass
class MyModel(DataClassTOMLMixin):
    ...

MyModel.from_toml(...)
MyModel(...).to_toml()
```

### MessagePack

[MessagePack](https://msgpack.org) is an efficient binary serialization format.
In order to use this mixin, the [`msgpack`](https://pypi.org/project/msgpack/)
package must be installed. You can install it manually or using an extra
option for `mashumaro`:

```shell
pip install mashumaro[msgpack]
```

The following data types will be handled by
[`msgpack`](https://pypi.org/project/msgpack/) library by default:
* [`bytes`](https://docs.python.org/3/library/stdtypes.html#bytes)
* [`bytearray`](https://docs.python.org/3/library/stdtypes.html#bytearray)

Efficient decoder and encoder can be used as follows:
```python
from mashumaro.codecs.msgpack import MessagePackDecoder, MessagePackEncoder

decoder = MessagePackDecoder(<shape_type>, ...)
decoder.decode(...)

encoder = MessagePackEncoder(<shape_type>, ...)
encoder.encode(...)
```

Convenient functions can be used as follows:
```python
from mashumaro.codecs.msgpack import msgpack_decode, msgpack_encode

msgpack_decode(..., <shape_type>)
msgpack_encode(..., <shape_type>)
```

Convenient function aliases are recommended to be used as follows:
```python
import mashumaro.codecs.msgpack as msgpack_codec

msgpack_codec.decode(...<shape_type>)
msgpack_codec.encode(..., <shape_type>)
```

Mixin can be used as follows:
```python
from mashumaro.mixins.msgpack import DataClassMessagePackMixin

@dataclass
class MyModel(DataClassMessagePackMixin):
    ...

MyModel.from_msgpack(...)
MyModel(...).to_msgpack()
```

Customization
-------------------------------------------------------------------------------

Customization options of `mashumaro` are extensive and will most likely cover your needs.
When it comes to non-standard data types and non-standard serialization support, you can do the following:
* Turn an existing regular or generic class into a serializable one
by inheriting the [`SerializableType`](#serializabletype-interface) class
* Write different serialization strategies for an existing regular or generic type that is not under your control
using [`SerializationStrategy`](#serializationstrategy) class
* Define serialization / deserialization methods:
  * for a specific dataclass field by using [field options](#field-options)
  * for a specific data type used in the dataclass by using [`Config`](#config-options) class
* Alter input and output data with serialization / deserialization [hooks](#serialization-hooks)
* Separate serialization scheme from a dataclass in a reusable manner using [dialects](#dialects)
* Choose from predefined serialization engines for the specific data types, e.g. `datetime` and `NamedTuple`

### SerializableType interface

If you have a custom class or hierarchy of classes whose instances you want
to serialize with `mashumaro`, the first option is to implement
`SerializableType` interface.

#### User-defined types

Let's look at this not very practicable example:

```python
from dataclasses import dataclass
from mashumaro import DataClassDictMixin
from mashumaro.types import SerializableType

class Airport(SerializableType):
    def __init__(self, code, city):
        self.code, self.city = code, city

    def _serialize(self):
        return [self.code, self.city]

    @classmethod
    def _deserialize(cls, value):
        return cls(*value)

    def __eq__(self, other):
        return self.code, self.city == other.code, other.city

@dataclass
class Flight(DataClassDictMixin):
    origin: Airport
    destination: Airport

JFK = Airport("JFK", "New York City")
LAX = Airport("LAX", "Los Angeles")

input_data = {
    "origin": ["JFK", "New York City"],
    "destination": ["LAX", "Los Angeles"]
}
my_flight = Flight.from_dict(input_data)
assert my_flight == Flight(JFK, LAX)
assert my_flight.to_dict() == input_data
```

You can see how `Airport` instances are seamlessly created from lists of two
strings and serialized into them.

By default `_deserialize` method will get raw input data without any
transformations before. This should be enough in many cases, especially when
you need to perform non-standard transformations yourself, but let's extend
our example:

```python
class Itinerary(SerializableType):
    def __init__(self, flights):
        self.flights = flights

    def _serialize(self):
        return self.flights

    @classmethod
    def _deserialize(cls, flights):
        return cls(flights)

@dataclass
class TravelPlan(DataClassDictMixin):
    budget: float
    itinerary: Itinerary

input_data = {
    "budget": 10_000,
    "itinerary": [
        {
            "origin": ["JFK", "New York City"],
            "destination": ["LAX", "Los Angeles"]
        },
        {
            "origin": ["LAX", "Los Angeles"],
            "destination": ["SFO", "San Fransisco"]
        }
    ]
}
```

If we pass the flight list as is into `Itinerary._deserialize`, our itinerary
will have something that we may not expect — `list[dict]` instead of
`list[Flight]`. The solution is quite simple. Instead of calling
`Flight._deserialize` yourself, just use annotations:

```python
class Itinerary(SerializableType, use_annotations=True):
    def __init__(self, flights):
        self.flights = flights

    def _serialize(self) -> list[Flight]:
        return self.flights

    @classmethod
    def _deserialize(cls, flights: list[Flight]):
        return cls(flights)

my_plan = TravelPlan.from_dict(input_data)
assert isinstance(my_plan.itinerary.flights[0], Flight)
assert isinstance(my_plan.itinerary.flights[1], Flight)
assert my_plan.to_dict() == input_data
```

Here we add annotations to the only argument of `_deserialize` method and
to the return value of `_serialize` method as well. The latter is needed for
correct serialization.

> [!IMPORTANT]\
> The importance of explicit passing `use_annotations=True` when defining a
> class is that otherwise implicit using annotations might break compatibility
> with old code that wasn't aware of this feature. It will be enabled by
> default in the future major release.

#### User-defined generic types

The great thing to note about using annotations in `SerializableType` is that
they work seamlessly with [generic](https://docs.python.org/3/library/typing.html#user-defined-generic-types)
and [variadic generic](https://peps.python.org/pep-0646/) types.
Let's see how this can be useful:

```python
from datetime import date
from typing import TypeVar
from dataclasses import dataclass
from mashumaro import DataClassDictMixin
from mashumaro.types import SerializableType

KT = TypeVar("KT")
VT = TypeVar("VT")

class DictWrapper(dict[KT, VT], SerializableType, use_annotations=True):
    def _serialize(self) -> dict[KT, VT]:
        return dict(self)

    @classmethod
    def _deserialize(cls, value: dict[KT, VT]) -> 'DictWrapper[KT, VT]':
        return cls(value)

@dataclass
class DataClass(DataClassDictMixin):
    x: DictWrapper[date, str]
    y: DictWrapper[str, date]

input_data = {
    "x": {"2022-12-07": "2022-12-07"},
    "y": {"2022-12-07": "2022-12-07"}
}
obj = DataClass.from_dict(input_data)
assert obj == DataClass(
    x=DictWrapper({date(2022, 12, 7): "2022-12-07"}),
    y=DictWrapper({"2022-12-07": date(2022, 12, 7)})
)
assert obj.to_dict() == input_data
```

You can see that formatted date is deserialized to `date` object before passing
to `DictWrapper._deserialize` in a key or value according to the generic
parameters.

If you have generic dataclass types, you can use `SerializableType` for them as well, but it's not necessary since
they're [supported](#generic-dataclasses) out of the box.

### SerializationStrategy

If you want to add support for a custom third-party type that is not under your control,
you can write serialization and deserialization logic inside `SerializationStrategy` class,
which will be reusable and so well suited in case that third-party type is widely used.
`SerializationStrategy` is also good if you want to create strategies that are slightly different from each other,
because you can add the strategy differentiator in the `__init__` method.

#### Third-party types

To demonstrate how `SerializationStrategy` works let's write a simple strategy for datetime serialization
in different formats. In this example we will use the same strategy class for two dataclass fields,
but a string representing the date and time will be different.

```python
from dataclasses import dataclass, field
from datetime import datetime
from mashumaro import DataClassDictMixin, field_options
from mashumaro.types import SerializationStrategy

class FormattedDateTime(SerializationStrategy):
    def __init__(self, fmt):
        self.fmt = fmt

    def serialize(self, value: datetime) -> str:
        return value.strftime(self.fmt)

    def deserialize(self, value: str) -> datetime:
        return datetime.strptime(value, self.fmt)

@dataclass
class DateTimeFormats(DataClassDictMixin):
    short: datetime = field(
        metadata=field_options(
            serialization_strategy=FormattedDateTime("%d%m%Y%H%M%S")
        )
    )
    verbose: datetime = field(
        metadata=field_options(
            serialization_strategy=FormattedDateTime("%A %B %d, %Y, %H:%M:%S")
        )
    )

formats = DateTimeFormats(
    short=datetime(2019, 1, 1, 12),
    verbose=datetime(2019, 1, 1, 12),
)
dictionary = formats.to_dict()
# {'short': '01012019120000', 'verbose': 'Tuesday January 01, 2019, 12:00:00'}
assert DateTimeFormats.from_dict(dictionary) == formats
```

Similarly to `SerializableType`, `SerializationStrategy` could also take advantage of annotations:

```python
from dataclasses import dataclass
from datetime import datetime
from mashumaro import DataClassDictMixin
from mashumaro.types import SerializationStrategy

class TsSerializationStrategy(SerializationStrategy, use_annotations=True):
    def serialize(self, value: datetime) -> float:
        return value.timestamp()

    def deserialize(self, value: float) -> datetime:
        # value will be converted to float before being passed to this method
        return datetime.fromtimestamp(value)

@dataclass
class Example(DataClassDictMixin):
    dt: datetime

    class Config:
        serialization_strategy = {
            datetime: TsSerializationStrategy(),
        }

example = Example.from_dict({"dt": "1672531200"})
print(example)
# Example(dt=datetime.datetime(2023, 1, 1, 3, 0))
print(example.to_dict())
# {'dt': 1672531200.0}
```

Here the passed string value `"1672531200"` will be converted to `float` before being passed to `deserialize` method
thanks to the `float` annotation.

> [!IMPORTANT]\
> As well as for `SerializableType`, the value of `use_annotatons` will be
> `True` by default in the future major release.

#### Third-party generic types

To create a generic version of a serialization strategy you need to follow these steps:
* inherit [`Generic[...]`](https://docs.python.org/3/library/typing.html#typing.Generic) type
with the number of parameters matching the number of parameters
of the target generic type
* Write generic annotations for `serialize` method's return type and for `deserialize` method's argument type
* Use the origin type of the target generic type in the [`serialization_strategy`](#serialization_strategy-config-option) config section
([`typing.get_origin`](https://docs.python.org/3/library/typing.html#typing.get_origin) might be helpful)

There is no need to add `use_annotations=True` here because it's enabled implicitly
for generic serialization strategies.

For example, there is a third-party [multidict](https://pypi.org/project/multidict/) package that has a generic `MultiDict` type.
A generic serialization strategy for it might look like this:

```python
from dataclasses import dataclass
from datetime import date
from pprint import pprint
from typing import Generic, List, Tuple, TypeVar
from mashumaro import DataClassDictMixin
from mashumaro.types import SerializationStrategy

from multidict import MultiDict

T = TypeVar("T")

class MultiDictSerializationStrategy(SerializationStrategy, Generic[T]):
    def serialize(self, value: MultiDict[T]) -> List[Tuple[str, T]]:
        return [(k, v) for k, v in value.items()]

    def deserialize(self, value: List[Tuple[str, T]]) -> MultiDict[T]:
        return MultiDict(value)


@dataclass
class Example(DataClassDictMixin):
    floats: MultiDict[float]
    date_lists: MultiDict[List[date]]

    class Config:
        serialization_strategy = {
            MultiDict: MultiDictSerializationStrategy()
        }

example = Example(
    floats=MultiDict([("x", 1.1), ("x", 2.2)]),
    date_lists=MultiDict(
        [("x", [date(2023, 1, 1), date(2023, 1, 2)]),
         ("x", [date(2023, 2, 1), date(2023, 2, 2)])]
    ),
)
pprint(example.to_dict())
# {'date_lists': [['x', ['2023-01-01', '2023-01-02']],
#                 ['x', ['2023-02-01', '2023-02-02']]],
#  'floats': [['x', 1.1], ['x', 2.2]]}
assert Example.from_dict(example.to_dict()) == example
```

### Field options

In some cases creating a new class just for one little thing could be
excessive. Moreover, you may need to deal with third party classes that you are
not allowed to change. You can use [`dataclasses.field`](https://docs.python.org/3/library/dataclasses.html#dataclasses.field) function to
configure some serialization aspects through its `metadata` parameter. Next
section describes all supported options to use in `metadata` mapping.

If you don't want to remember the names of the options you can use
`field_options` helper function:

```python
from dataclasses import dataclass, field
from mashumaro import field_options

@dataclass
class A:
    x: int = field(metadata=field_options(...))
```

#### `serialize` option

This option allows you to change the serialization method. When using
this option, the serialization behaviour depends on what type of value the
option has. It could be either `Callable[[Any], Any]` or `str`.

A value of type `Callable[[Any], Any]` is a generic way to specify any callable
object like a function, a class method, a class instance method, an instance
of a callable class or even a lambda function to be called for serialization.

A value of type `str` sets a specific engine for serialization. Keep in mind
that all possible engines depend on the data type that this option is used
with. At this moment there are next serialization engines to choose from:

| Applicable data types      | Supported engines    | Description                                                                                                                                                                                                  |
|:---------------------------|:---------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `NamedTuple`, `namedtuple` | `as_list`, `as_dict` | How to pack named tuples. By default `as_list` engine is used that means your named tuple class instance will be packed into a list of its values. You can pack it into a dictionary using `as_dict` engine. |
| `Any`                      | `omit`               | Skip the field during serialization                                                                                                                                                                          |

> [!TIP]\
> You can pass a field value as is without changes on serialization using
[`pass_through`](#passing-field-values-as-is).

Example:

```python
from datetime import datetime
from dataclasses import dataclass, field
from typing import NamedTuple
from mashumaro import DataClassDictMixin

class MyNamedTuple(NamedTuple):
    x: int
    y: float

@dataclass
class A(DataClassDictMixin):
    dt: datetime = field(
        metadata={
            "serialize": lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }
    )
    t: MyNamedTuple = field(metadata={"serialize": "as_dict"})
```

#### `deserialize` option

This option allows you to change the deserialization method. When using
this option, the deserialization behaviour depends on what type of value the
option has. It could be either `Callable[[Any], Any]` or `str`.

A value of type `Callable[[Any], Any]` is a generic way to specify any callable
object like a function, a class method, a class instance method, an instance
of a callable class or even a lambda function to be called for deserialization.

A value of type `str` sets a specific engine for deserialization. Keep in mind
that all possible engines depend on the data type that this option is used
with. At this moment there are next deserialization engines to choose from:

| Applicable data types      | Supported engines                                                                                                                   | Description                                                                                                                                                                                                                                                                                             |
|:---------------------------|:------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `datetime`, `date`, `time` | [`ciso8601`](https://github.com/closeio/ciso8601#supported-subset-of-iso-8601), [`pendulum`](https://github.com/sdispater/pendulum) | How to parse datetime string. By default native [`fromisoformat`](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat) of corresponding class will be used for `datetime`, `date` and `time` fields. It's the fastest way in most cases, but you can choose an alternative. |
| `NamedTuple`, `namedtuple` | `as_list`, `as_dict`                                                                                                                | How to unpack named tuples. By default `as_list` engine is used that means your named tuple class instance will be created from a list of its values. You can unpack it from a dictionary using `as_dict` engine.                                                                                       |

> [!TIP]\
> You can pass a field value as is without changes on deserialization using
[`pass_through`](#passing-field-values-as-is).

Example:

```python
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, NamedTuple
from mashumaro import DataClassDictMixin
import ciso8601
import dateutil

class MyNamedTuple(NamedTuple):
    x: int
    y: float

@dataclass
class A(DataClassDictMixin):
    x: datetime = field(
        metadata={"deserialize": "pendulum"}
    )

class B(DataClassDictMixin):
    x: datetime = field(
        metadata={"deserialize": ciso8601.parse_datetime_as_naive}
    )

@dataclass
class C(DataClassDictMixin):
    dt: List[datetime] = field(
        metadata={
            "deserialize": lambda l: list(map(dateutil.parser.isoparse, l))
        }
    )

@dataclass
class D(DataClassDictMixin):
    x: MyNamedTuple = field(metadata={"deserialize": "as_dict"})
```

#### `serialization_strategy` option

This option is useful when you want to change the serialization logic
for a dataclass field depending on some defined parameters using a reusable
serialization scheme. You can find an example in the
[`SerializationStrategy`](#serializationstrategy) chapter.

> [!TIP]\
> You can pass a field value as is without changes on
> serialization / deserialization using
[`pass_through`](#passing-field-values-as-is).

#### `alias` option

This option can be used to assign [field aliases](#field-aliases):


```python
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin, field_options

@dataclass
class DataClass(DataClassDictMixin):
    a: int = field(metadata=field_options(alias="FieldA"))
    b: int = field(metadata=field_options(alias="#invalid"))

x = DataClass.from_dict({"FieldA": 1, "#invalid": 2})  # DataClass(a=1, b=2)
```

### Config options

If inheritance is not an empty word for you, you'll fall in love with the
`Config` class. You can register `serialize` and `deserialize` methods, define
code generation options and other things just in one place. Or in some
classes in different ways if you need flexibility. Inheritance is always on the
first place.

There is a base class `BaseConfig` that you can inherit for the sake of
convenience, but it's not mandatory.

In the following example you can see how
the `debug` flag is changed from class to class: `ModelA` will have debug mode enabled but
`ModelB` will not.

```python
from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig

class BaseModel(DataClassDictMixin):
    class Config(BaseConfig):
        debug = True

class ModelA(BaseModel):
    a: int

class ModelB(BaseModel):
    b: int

    class Config(BaseConfig):
        debug = False
```

Next section describes all supported options to use in the config.

#### `debug` config option

If you enable the `debug` option the generated code for your data class
will be printed.

#### `code_generation_options` config option

Some users may need functionality that wouldn't exist without extra cost such
as valuable cpu time to execute additional instructions. Since not everyone
needs such instructions, they can be enabled by a constant in the list,
so the fastest basic behavior of the library will always remain by default.
The following table provides a brief overview of all the available constants
described below.

| Constant                                                        | Description                                                          |
|:----------------------------------------------------------------|:---------------------------------------------------------------------|
| [`TO_DICT_ADD_OMIT_NONE_FLAG`](#add-omit_none-keyword-argument) | Adds `omit_none` keyword-only argument to `to_*` methods.            |
| [`TO_DICT_ADD_BY_ALIAS_FLAG`](#add-by_alias-keyword-argument)   | Adds `by_alias` keyword-only argument to `to_*` methods.             |
| [`ADD_DIALECT_SUPPORT`](#add-dialect-keyword-argument)          | Adds `dialect` keyword-only argument to `from_*` and `to_*` methods. |
| [`ADD_SERIALIZATION_CONTEXT`](#add-context-keyword-argument)    | Adds `context` keyword-only argument to `to_*` methods.              |

#### `serialization_strategy` config option

You can register custom [`SerializationStrategy`](#serializationstrategy), `serialize` and `deserialize`
methods for specific types just in one place. It could be configured using
a dictionary with types as keys. The value could be either a
[`SerializationStrategy`](#serializationstrategy) instance or a dictionary with `serialize` and
`deserialize` values with the same meaning as in the
[field options](#field-options).

```python
from dataclasses import dataclass
from datetime import datetime, date
from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig
from mashumaro.types import SerializationStrategy

class FormattedDateTime(SerializationStrategy):
    def __init__(self, fmt):
        self.fmt = fmt

    def serialize(self, value: datetime) -> str:
        return value.strftime(self.fmt)

    def deserialize(self, value: str) -> datetime:
        return datetime.strptime(value, self.fmt)

@dataclass
class DataClass(DataClassDictMixin):

    x: datetime
    y: date

    class Config(BaseConfig):
        serialization_strategy = {
            datetime: FormattedDateTime("%Y"),
            date: {
                # you can use specific str values for datetime here as well
                "deserialize": "pendulum",
                "serialize": date.isoformat,
            },
        }

instance = DataClass.from_dict({"x": "2021", "y": "2021"})
# DataClass(x=datetime.datetime(2021, 1, 1, 0, 0), y=Date(2021, 1, 1))
dictionary = instance.to_dict()
# {'x': '2021', 'y': '2021-01-01'}
```

Note that you can register different methods for multiple logical types which
are based on the same type using `NewType` and `Annotated`,
see [Extending existing types](#extending-existing-types) for details.

It's also possible to define a generic (de)serialization method for a generic
type by registering a method for its
[origin](https://docs.python.org/3/library/typing.html#typing.get_origin) type.
Although this technique is widely used when working with [third-party generic
types](#third-party-generic-types) using generic strategies, it can also be
applied in simple scenarios:

```python
from dataclasses import dataclass
from mashumaro import DataClassDictMixin

@dataclass
class C(DataClassDictMixin):
    ints: list[int]
    floats: list[float]

    class Config:
        serialization_strategy = {
            list: {  # origin type for list[int] and list[float] is list
                "serialize": lambda x: list(map(str, x)),
            }
        }

assert C([1], [2.2]).to_dict() == {'ints': ['1'], 'floats': ['2.2']}
```

#### `aliases` config option

Sometimes it's better to write the [field aliases](#field-aliases) in one place. You can mix
aliases here with [aliases in the field options](#alias-option), but the last ones will always
take precedence.

```python
from dataclasses import dataclass
from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig

@dataclass
class DataClass(DataClassDictMixin):
    a: int
    b: int

    class Config(BaseConfig):
        aliases = {
            "a": "FieldA",
            "b": "FieldB",
        }

DataClass.from_dict({"FieldA": 1, "FieldB": 2})  # DataClass(a=1, b=2)
```

#### `serialize_by_alias` config option

All the fields with [aliases](#field-aliases) will be serialized by them by
default when this option is enabled. You can mix this config option with
[`by_alias`](#add-by_alias-keyword-argument) keyword argument.

```python
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin, field_options
from mashumaro.config import BaseConfig

@dataclass
class DataClass(DataClassDictMixin):
    field_a: int = field(metadata=field_options(alias="FieldA"))

    class Config(BaseConfig):
        serialize_by_alias = True

DataClass(field_a=1).to_dict()  # {'FieldA': 1}
```

#### `allow_deserialization_not_by_alias` config option

When using aliases, the deserializer defaults to requiring the keys to match
what is defined as the alias.
If the flexibility to deserialize aliased and unaliased keys is required then
the config option `allow_deserialization_not_by_alias ` can be set to
enable the feature.

```python
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig


@dataclass
class AliasedDataClass(DataClassDictMixin):
    foo: int = field(metadata={"alias": "alias_foo"})
    bar: int = field(metadata={"alias": "alias_bar"})

    class Config(BaseConfig):
        allow_deserialization_not_by_alias = True


alias_dict = {"alias_foo": 1, "alias_bar": 2}
t1 = AliasedDataClass.from_dict(alias_dict)

no_alias_dict = {"foo": 1, "bar": 2}
# This would raise `mashumaro.exceptions.MissingField`
# if allow_deserialization_not_by_alias was False
t2 = AliasedDataClass.from_dict(no_alias_dict)
assert t1 == t2
```

#### `omit_none` config option

All the fields with `None` values will be skipped during serialization by
default when this option is enabled. You can mix this config option with
[`omit_none`](#add-omit_none-keyword-argument) keyword argument.

```python
from dataclasses import dataclass
from typing import Optional
from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig

@dataclass
class DataClass(DataClassDictMixin):
    x: Optional[int] = 42

    class Config(BaseConfig):
        omit_none = True

DataClass(x=None).to_dict()  # {}
```

#### `omit_default` config option

When this option enabled, all the fields that have values equal to the defaults
or the default_factory results will be skipped during serialization.

```python
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from mashumaro import DataClassDictMixin, field_options
from mashumaro.config import BaseConfig

@dataclass
class Foo:
    foo: str

@dataclass
class DataClass(DataClassDictMixin):
    a: int = 42
    b: Tuple[int, ...] = field(default=(1, 2, 3))
    c: List[Foo] = field(default_factory=lambda: [Foo("foo")])
    d: Optional[str] = None

    class Config(BaseConfig):
        omit_default = True

DataClass(a=42, b=(1, 2, 3), c=[Foo("foo")]).to_dict()  # {}
```

#### `namedtuple_as_dict` config option

Dataclasses are a great way to declare and use data models. But it's not the only way.
Python has a typed version of [namedtuple](https://docs.python.org/3/library/collections.html#collections.namedtuple)
called [NamedTuple](https://docs.python.org/3/library/typing.html#typing.NamedTuple)
which looks similar to dataclasses:

```python
from typing import NamedTuple

class Point(NamedTuple):
    x: int
    y: int
```

the same with a dataclass will look like this:

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int
```

At first glance, you can use both options. But imagine that you need to create
a bunch of instances of the `Point` class. Due to how dataclasses work you will
have more memory consumption compared to named tuples. In such a case it could
be more appropriate to use named tuples.

By default, all named tuples are packed into lists. But with `namedtuple_as_dict`
option you have a drop-in replacement for dataclasses:

```python
from dataclasses import dataclass
from typing import List, NamedTuple
from mashumaro import DataClassDictMixin

class Point(NamedTuple):
    x: int
    y: int

@dataclass
class DataClass(DataClassDictMixin):
    points: List[Point]

    class Config:
        namedtuple_as_dict = True

obj = DataClass.from_dict({"points": [{"x": 0, "y": 0}, {"x": 1, "y": 1}]})
print(obj.to_dict())  # {"points": [{"x": 0, "y": 0}, {"x": 1, "y": 1}]}
```

If you want to serialize only certain named tuple fields as dictionaries, you
can use the corresponding [serialization](#serialize-option) and
[deserialization](#deserialize-option) engines.

#### `allow_postponed_evaluation` config option

[PEP 563](https://www.python.org/dev/peps/pep-0563/) solved the problem of forward references by postponing the evaluation
of annotations, so you can write the following code:

```python
from __future__ import annotations
from dataclasses import dataclass
from mashumaro import DataClassDictMixin

@dataclass
class A(DataClassDictMixin):
    x: B

@dataclass
class B(DataClassDictMixin):
    y: int

obj = A.from_dict({'x': {'y': 1}})
```

You don't need to write anything special here, forward references work out of
the box. If a field of a dataclass has a forward reference in the type
annotations, building of `from_*` and `to_*` methods of this dataclass
will be postponed until they are called once. However, if for some reason you
don't want the evaluation to be possibly postponed, you can disable it using
`allow_postponed_evaluation` option:

```python
from __future__ import annotations
from dataclasses import dataclass
from mashumaro import DataClassDictMixin

@dataclass
class A(DataClassDictMixin):
    x: B

    class Config:
        allow_postponed_evaluation = False

# UnresolvedTypeReferenceError: Class A has unresolved type reference B
# in some of its fields

@dataclass
class B(DataClassDictMixin):
    y: int
```

In this case you will get `UnresolvedTypeReferenceError` regardless of whether
class B is declared below or not.

#### `dialect` config option

This option is described [below](#changing-the-default-dialect) in the
Dialects section.

#### `orjson_options` config option

This option changes default options for `orjson.dumps` encoder which is
used in [`DataClassORJSONMixin`](#dataclassorjsonmixin). For example, you can
tell orjson to handle non-`str` `dict` keys as the built-in `json.dumps`
encoder does. See [orjson documentation](https://github.com/ijl/orjson#option)
to read more about these options.

```python
import orjson
from dataclasses import dataclass
from typing import Dict
from mashumaro.config import BaseConfig
from mashumaro.mixins.orjson import DataClassORJSONMixin

@dataclass
class MyClass(DataClassORJSONMixin):
    x: Dict[int, int]

    class Config(BaseConfig):
        orjson_options = orjson.OPT_NON_STR_KEYS

assert MyClass({1: 2}).to_json() == {"1": 2}
```

#### `discriminator` config option

This option is described in the
[Class level discriminator](#class-level-discriminator) section.

#### `lazy_compilation` config option

By using this option, the compilation of the `from_*` and `to_*` methods will
be deferred until they are called first time. This will reduce the import time
and, in certain instances, may enhance the speed of deserialization
by leveraging the data that is accessible after the class has been created.

> [!CAUTION]\
> If you need to save a reference to `from_*` or `to_*` method, you should
> do it after the method is compiled. To be safe, you can always use lambda
> function:
> ```python
> from_dict = lambda x: MyModel.from_dict(x)
> to_dict = lambda x: x.to_dict()
> ```

#### `sort_keys` config option

When set, the keys on serialized dataclasses will be sorted in alphabetical order.

Unlike the `sort_keys` option in the standard library's `json.dumps` function, this option acts at class creation time and has no effect on the performance of serialization.

```python
from dataclasses import dataclass
from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig

@dataclass
class SortedDataClass(DataClassDictMixin):
    foo: int
    bar: int

    class Config(BaseConfig):
        sort_keys = True

t = SortedDataClass(1, 2)
assert t.to_dict() == {"bar": 2, "foo": 1}
```

#### `forbid_extra_keys` config option

When set, the deserialization of dataclasses will fail if the input dictionary contains keys that are not present in the dataclass.

```python
from dataclasses import dataclass
from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig

@dataclass
class DataClass(DataClassDictMixin):
    a: int

    class Config(BaseConfig):
        forbid_extra_keys = True

DataClass.from_dict({"a": 1, "b": 2})  # ExtraKeysError: Extra keys: {'b'}
```

It plays well with `aliases` and `allow_deserialization_not_by_alias` options.

### Passing field values as is

In some cases it's needed to pass a field value as is without any changes
during serialization / deserialization. There is a predefined
[`pass_through`](https://github.com/Fatal1ty/mashumaro/blob/master/mashumaro/helper.py#L58)
object that can be used as `serialization_strategy` or
`serialize` / `deserialize` options:

```python
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin, pass_through

class MyClass:
    def __init__(self, some_value):
        self.some_value = some_value

@dataclass
class A1(DataClassDictMixin):
    x: MyClass = field(
        metadata={
            "serialize": pass_through,
            "deserialize": pass_through,
        }
    )

@dataclass
class A2(DataClassDictMixin):
    x: MyClass = field(
        metadata={
            "serialization_strategy": pass_through,
        }
    )

@dataclass
class A3(DataClassDictMixin):
    x: MyClass

    class Config:
        serialization_strategy = {
            MyClass: pass_through,
        }

@dataclass
class A4(DataClassDictMixin):
    x: MyClass

    class Config:
        serialization_strategy = {
            MyClass: {
                "serialize": pass_through,
                "deserialize": pass_through,
            }
        }

my_class_instance = MyClass(42)

assert A1.from_dict({'x': my_class_instance}).x == my_class_instance
assert A2.from_dict({'x': my_class_instance}).x == my_class_instance
assert A3.from_dict({'x': my_class_instance}).x == my_class_instance
assert A4.from_dict({'x': my_class_instance}).x == my_class_instance

a1_dict = A1(my_class_instance).to_dict()
a2_dict = A2(my_class_instance).to_dict()
a3_dict = A3(my_class_instance).to_dict()
a4_dict = A4(my_class_instance).to_dict()

assert a1_dict == a2_dict == a3_dict == a4_dict == {"x": my_class_instance}
```

### Extending existing types

There are situations where you might want some values of the same type to be
treated as their own type. You can create new logical types with
[`NewType`](https://docs.python.org/3/library/typing.html#newtype),
[`Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated)
or [`TypeAliasType`](https://docs.python.org/3/library/typing.html#typing.TypeAliasType)
and register serialization strategies for them:

```python
from typing import Mapping, NewType, Annotated
from dataclasses import dataclass
from mashumaro import DataClassDictMixin

SessionID = NewType("SessionID", str)
AccountID = Annotated[str, "AccountID"]

type DeviceID = str

@dataclass
class Context(DataClassDictMixin):
    account_sessions: Mapping[AccountID, SessionID]
    account_devices: list[DeviceID]

    class Config:
        serialization_strategy = {
            AccountID: {
                "deserialize": lambda x: ...,
                "serialize": lambda x: ...,
            },
            SessionID: {
                "deserialize": lambda x: ...,
                "serialize": lambda x: ...,
            },
            DeviceID: {
                "deserialize": lambda x: ...,
                "serialize": lambda x: ...,
            }
        }
```

Although using `NewType` is usually the most reliable way to avoid logical
errors, you have to pay for it with notable overhead. If you are creating
dataclass instances manually, then you know that type checkers will
enforce you to enclose a value in your `"NewType"` callable, which leads
to performance degradation:

```python
python -m timeit -s "from typing import NewType; MyInt = NewType('MyInt', int)" "MyInt(42)"
10000000 loops, best of 5: 31.1 nsec per loop

python -m timeit -s "from typing import NewType; MyInt = NewType('MyInt', int)" "42"
50000000 loops, best of 5: 4.35 nsec per loop
```

However, when you create dataclass instances using the `from_*` method provided
by one of the mixins or using one of the decoders, there will be no performance
degradation, because the value won't be enclosed in the callable in the
generated code. Therefore, if performance is more important to you than
catching logical errors by type checkers, and you are actively creating or
changing dataclasses manually, then you should take a closer look at using
`Annotated`.

### Field aliases

In some cases it's better to have different names for a field in your dataclass
and in its serialized view. For example, a third-party legacy API you are
working with might operate with camel case style, but you stick to snake case
style in your code base. Or you want to load data with keys that are
invalid identifiers in Python. Aliases can solve this problem.

There are multiple ways to assign an alias:
* Using `Alias(...)` annotation in a field type
* Using `alias` parameter in field metadata
* Using `aliases` parameter in a dataclass config

By default, aliases only affect deserialization, but it can be extended to
serialization as well. If you want to serialize all the fields by aliases you
have two options to do so:
* [`serialize_by_alias` config option](#serialize_by_alias-config-option)
* [`serialize_by_alias` dialect option](#serialize_by_alias-dialect-option)
* [`by_alias` keyword argument in `to_*` methods](#add-by_alias-keyword-argument)

Here is an example with `Alias` annotation in a field type:

```python
from dataclasses import dataclass
from typing import Annotated
from mashumaro import DataClassDictMixin
from mashumaro.types import Alias

@dataclass
class DataClass(DataClassDictMixin):
    foo_bar: Annotated[int, Alias("fooBar")]

obj = DataClass.from_dict({"fooBar": 42})  # DataClass(foo_bar=42)
obj.to_dict()  # {"foo_bar": 42}  # no aliases on serialization by default
```

The same with field metadata:

```python
from dataclasses import dataclass, field
from mashumaro import field_options

@dataclass
class DataClass:
    foo_bar: str = field(metadata=field_options(alias="fooBar"))
```

And with a dataclass config:

```python
from dataclasses import dataclass
from mashumaro.config import BaseConfig

@dataclass
class DataClass:
    foo_bar: str

    class Config(BaseConfig):
        aliases = {"foo_bar": "fooBar"}
```

> [!TIP]\
> If you want to deserialize all the fields by its names along with aliases,
> there is [a config option](#allow_deserialization_not_by_alias-config-option)
> for that.

### Dialects

Sometimes it's needed to have different serialization and deserialization
methods depending on the data source where entities of the dataclass are
stored or on the API to which the entities are being sent or received from.
There is a special `Dialect` type that may contain all the differences from the
default serialization and deserialization methods. You can create different
dialects and use each of them for the same dataclass depending on
the situation.

Suppose we have the following dataclass with a field of type `date`:
```python
@dataclass
class Entity(DataClassDictMixin):
    dt: date
```

By default, a field of `date` type serializes to a string in ISO 8601 format,
so the serialized entity will look like `{'dt': '2021-12-31'}`. But what if we
have, for example, two sensitive legacy Ethiopian and Japanese APIs that use
two different formats for dates — `dd/mm/yyyy` and `yyyy年mm月dd日`? Instead of
creating two similar dataclasses we can have one dataclass and two dialects:
```python
from dataclasses import dataclass
from datetime import date, datetime
from mashumaro import DataClassDictMixin
from mashumaro.config import ADD_DIALECT_SUPPORT
from mashumaro.dialect import Dialect
from mashumaro.types import SerializationStrategy

class DateTimeSerializationStrategy(SerializationStrategy):
    def __init__(self, fmt: str):
        self.fmt = fmt

    def serialize(self, value: date) -> str:
        return value.strftime(self.fmt)

    def deserialize(self, value: str) -> date:
        return datetime.strptime(value, self.fmt).date()

class EthiopianDialect(Dialect):
    serialization_strategy = {
        date: DateTimeSerializationStrategy("%d/%m/%Y")
    }

class JapaneseDialect(Dialect):
    serialization_strategy = {
        date: DateTimeSerializationStrategy("%Y年%m月%d日")
    }

@dataclass
class Entity(DataClassDictMixin):
    dt: date

    class Config:
        code_generation_options = [ADD_DIALECT_SUPPORT]

entity = Entity(date(2021, 12, 31))
entity.to_dict(dialect=EthiopianDialect)  # {'dt': '31/12/2021'}
entity.to_dict(dialect=JapaneseDialect)   # {'dt': '2021年12月31日'}
Entity.from_dict({'dt': '2021年12月31日'}, dialect=JapaneseDialect)
```

#### `serialization_strategy` dialect option

This dialect option has the same meaning as the
[similar config option](#serialization_strategy-config-option)
but for the dialect scope. You can register custom [`SerializationStrategy`](#serializationstrategy),
`serialize` and `deserialize` methods for the specific types.

#### `serialize_by_alias` dialect option

This dialect option has the same meaning as the
[similar config option](#serialize_by_alias-config-option)
but for the dialect scope.

#### `omit_none` dialect option

This dialect option has the same meaning as the
[similar config option](#omit_none-config-option) but for the dialect scope.

#### `omit_default` dialect option

This dialect option has the same meaning as the
[similar config option](#omitdefault-config-option) but for the dialect scope.

#### `namedtuple_as_dict` dialect option

This dialect option has the same meaning as the
[similar config option](#namedtuple_as_dict-config-option)
but for the dialect scope.

#### `no_copy_collections` dialect option

By default, all collection data types are serialized as a copy to prevent
mutation of the original collection. As an example, if a dataclass contains
a field of type `list[str]`, then it will be serialized as a copy of the
original list, so you can safely mutate it after. The downside is that copying
is always slower than using a reference to the original collection. In some
cases we know beforehand that mutation doesn't take place or is even desirable,
so we can benefit from avoiding unnecessary copies by setting
`no_copy_collections` to a sequence of origin collection data types.
This is applicable only for collections containing elements that do not
require conversion.

```python
from dataclasses import dataclass
from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig
from mashumaro.dialect import Dialect

class NoCopyDialect(Dialect):
    no_copy_collections = (list, dict, set)

@dataclass
class DataClass(DataClassDictMixin):
    simple_list: list[str]
    simple_dict: dict[str, str]
    simple_set: set[str]

    class Config(BaseConfig):
        dialect = NoCopyDialect

obj = DataClass(["foo"], {"bar": "baz"}, {"foobar"})
data = obj.to_dict()

assert data["simple_list"] is obj.simple_list
assert data["simple_dict"] is obj.simple_dict
assert data["simple_set"] is obj.simple_set
```

This option is enabled for `list` and `dict` in the default dialects that
belong to mixins and codecs for the following formats:
* [JSON (orjson library)](#orjson-library)
* [TOML](#toml)
* [MessagePack](#messagepack)

#### Changing the default dialect

You can change the default serialization and deserialization methods not only
in the [`serialization_strategy`](#serialization_strategy-config-option) config
option but also using the `dialect` config option. If you have multiple
dataclasses without a common parent class the default dialect can help you
to reduce the number of code lines written:

```python
@dataclass
class Entity(DataClassDictMixin):
    dt: date

    class Config:
        dialect = JapaneseDialect

entity = Entity(date(2021, 12, 31))
entity.to_dict()  # {'dt': '2021年12月31日'}
assert Entity.from_dict({'dt': '2021年12月31日'}) == entity
```

Default dialect can also be set when using codecs:
```python
from mashumaro.codecs import BasicDecoder, BasicEncoder

@dataclass
class Entity:
    dt: date

decoder = BasicDecoder(Entity, default_dialect=JapaneseDialect)
encoder = BasicEncoder(Entity, default_dialect=JapaneseDialect)

entity = Entity(date(2021, 12, 31))
encoder.encode(entity) # {'dt': '2021年12月31日'}
assert decoder.decode({'dt': '2021年12月31日'}) == entity
```

### Discriminator

There is a special `Discriminator` class that allows you to customize how
a union of dataclasses or their hierarchy will be deserialized.
It has the following parameters that affects class selection rules:

* `field` — optional name of the input dictionary key (also known as tag)
  by which all the variants can be distinguished
* `include_subtypes` — allow to deserialize subclasses
* `include_supertypes` — allow to deserialize superclasses
* `variant_tagger_fn` — a custom function used to generate tag values
  associated with a variant

By default, each variant that you want to discriminate by tags should have a
class-level attribute containing an associated tag value. This attribute should
have a name defined by `field` parameter. The tag value coule be in the
following forms:

* without annotations: `type = 42`
* annotated as ClassVar: `type: ClassVar[int] = 42`
* annotated as Final: `type: Final[int] = 42`
* annotated as Literal: `type: Literal[42] = 42`
* annotated as StrEnum: `type: ResponseType = ResponseType.OK`

> [!NOTE]\
> Keep in mind that by default only Final, Literal and StrEnum fields are
> processed during serialization.

However, it is possible to use discriminator without the class-level
attribute. You can provide a custom function that generates one or many variant
tag values. This function should take a class as the only argument and return
either a single value of the basic type like `str` or `int` or a list of them
to associate multiple tags with a variant. The common practice is to use
a class name as a single tag value:

```python
variant_tagger_fn = lambda cls: cls.__name__
```

Next, we will look at different use cases, as well as their pros and cons.

#### Subclasses distinguishable by a field

Often you have a base dataclass and multiple subclasses that are easily
distinguishable from each other by the value of a particular field.
For example, there may be different events, messages or requests with
a discriminator field "event_type", "message_type" or just "type". You could've
listed all of them within `Union` type, but it would be too verbose and
impractical. Moreover, deserialization of the union would be slow, since we
need to iterate over each variant in the list until we find the right one.

We can improve subclass deserialization using `Discriminator` as annotation
within `Annotated` type. We will use `field` parameter and set
`include_subtypes` to `True`.

> [!IMPORTANT]\
> The discriminator field should be accessible from the `__dict__` attribute
> of a specific descendant, i.e. defined at the level of that descendant.
> A descendant class without a discriminator field will be ignored, but
> its descendants won't.

Suppose we have a hierarchy of client events distinguishable by a class
attribute "type":

```python
from dataclasses import dataclass
from ipaddress import IPv4Address
from mashumaro import DataClassDictMixin

@dataclass
class ClientEvent(DataClassDictMixin):
    pass

@dataclass
class ClientConnectedEvent(ClientEvent):
    type = "connected"
    client_ip: IPv4Address

@dataclass
class ClientDisconnectedEvent(ClientEvent):
    type = "disconnected"
    client_ip: IPv4Address
```

We use base dataclass `ClientEvent` for a field of another dataclass:

```python
from typing import Annotated, List
# or from typing_extensions import Annotated
from mashumaro.types import Discriminator


@dataclass
class AggregatedEvents(DataClassDictMixin):
    list: List[
        Annotated[
            ClientEvent, Discriminator(field="type", include_subtypes=True)
        ]
    ]
```

Now we can deserialize events based on "type" value:

```python
events = AggregatedEvents.from_dict(
    {
        "list": [
            {"type": "connected", "client_ip": "10.0.0.42"},
            {"type": "disconnected", "client_ip": "10.0.0.42"},
        ]
    }
)
assert events == AggregatedEvents(
    list=[
        ClientConnectedEvent(client_ip=IPv4Address("10.0.0.42")),
        ClientDisconnectedEvent(client_ip=IPv4Address("10.0.0.42")),
    ]
)
```

#### Subclasses without a common field

In rare cases you have to deal with subclasses that don't have a common field
name which they can be distinguished by. Since `Discriminator` can be
initialized without "field" parameter you can use it with only
`include_subclasses` enabled. The drawback is that we will have to go through all
the subclasses until we find the suitable one. It's almost like using `Union`
type but with subclasses support.

Suppose we're making a brunch. We have some ingredients:

```python
@dataclass
class Ingredient(DataClassDictMixin):
    name: str

@dataclass
class Hummus(Ingredient):
    made_of: Literal["chickpeas", "beet", "artichoke"]
    grams: int

@dataclass
class Celery(Ingredient):
    pieces: int
```

Let's create a plate:

```python
@dataclass
class Plate(DataClassDictMixin):
    ingredients: List[
        Annotated[Ingredient, Discriminator(include_subtypes=True)]
    ]
```

And now we can put our ingredients on the plate:

```python
plate = Plate.from_dict(
    {
        "ingredients": [
            {
                "name": "hummus from the shop",
                "made_of": "chickpeas",
                "grams": 150,
            },
            {"name": "celery from my garden", "pieces": 5},
        ]
    }
)
assert plate == Plate(
    ingredients=[
        Hummus(name="hummus from the shop", made_of="chickpeas", grams=150),
        Celery(name="celery from my garden", pieces=5),
    ]
)
```

In some cases it's necessary to fall back to the base class if there is no
suitable subclass. We can set `include_supertypes` to `True`:

```python
@dataclass
class Plate(DataClassDictMixin):
    ingredients: List[
        Annotated[
            Ingredient,
            Discriminator(include_subtypes=True, include_supertypes=True),
        ]
    ]

plate = Plate.from_dict(
    {
        "ingredients": [
            {
                "name": "hummus from the shop",
                "made_of": "chickpeas",
                "grams": 150,
            },
            {"name": "celery from my garden", "pieces": 5},
            {"name": "cumin"}  # <- new unknown ingredient
        ]
    }
)
assert plate == Plate(
    ingredients=[
        Hummus(name="hummus from the shop", made_of="chickpeas", grams=150),
        Celery(name="celery from my garden", pieces=5),
        Ingredient(name="cumin"),  # <- unknown ingredient added
    ]
)
```

#### Class level discriminator

It may often be more convenient to specify a `Discriminator` once at the class
level and use that class without `Annotated` type for subclass deserialization.
Depending on the `Discriminator` parameters, it can be used as a replacement for
[subclasses distinguishable by a field](#subclasses-distinguishable-by-a-field)
as well as for [subclasses without a common field](#subclasses-without-a-common-field).
The only difference is that you can't use `include_supertypes=True` because
it would lead to a recursion error.

Reworked example will look like this:

```python
from dataclasses import dataclass
from ipaddress import IPv4Address
from typing import List
from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig
from mashumaro.types import Discriminator

@dataclass
class ClientEvent(DataClassDictMixin):
    class Config(BaseConfig):
        discriminator = Discriminator(  # <- add discriminator
            field="type",
            include_subtypes=True,
        )

@dataclass
class ClientConnectedEvent(ClientEvent):
    type = "connected"
    client_ip: IPv4Address

@dataclass
class ClientDisconnectedEvent(ClientEvent):
    type = "disconnected"
    client_ip: IPv4Address

@dataclass
class AggregatedEvents(DataClassDictMixin):
    list: List[ClientEvent]  # <- use base class here
```

And now we can deserialize events based on "type" value as we did earlier:

```python
events = AggregatedEvents.from_dict(
    {
        "list": [
            {"type": "connected", "client_ip": "10.0.0.42"},
            {"type": "disconnected", "client_ip": "10.0.0.42"},
        ]
    }
)
assert events == AggregatedEvents(
    list=[
        ClientConnectedEvent(client_ip=IPv4Address("10.0.0.42")),
        ClientDisconnectedEvent(client_ip=IPv4Address("10.0.0.42")),
    ]
)
```

What's more interesting is that you can now deserialize subclasses simply by
calling the superclass `from_*` method, which is very useful:
```python
disconnected_event = ClientEvent.from_dict(
    {"type": "disconnected", "client_ip": "10.0.0.42"}
)
assert disconnected_event == ClientDisconnectedEvent(IPv4Address("10.0.0.42"))
```

The same is applicable for subclasses without a common field:

```python
@dataclass
class Ingredient(DataClassDictMixin):
    name: str

    class Config:
        discriminator = Discriminator(include_subtypes=True)

...

celery = Ingredient.from_dict({"name": "celery from my garden", "pieces": 5})
assert celery == Celery(name="celery from my garden", pieces=5)
```

#### Working with union of classes

Deserialization of union of types distinguishable by a particular field will
be much faster using `Discriminator` because there will be no traversal
of all classes and an attempt to deserialize each of them.
Usually this approach can be used when you have multiple classes without a
common superclass or when you only need to deserialize some of the subclasses.
In the following example we will use `include_supertypes=True` to
deserialize two subclasses out of three:

```python
from dataclasses import dataclass
from typing import Annotated, Literal, Union
# or from typing_extensions import Annotated
from mashumaro import DataClassDictMixin
from mashumaro.types import Discriminator

@dataclass
class Event(DataClassDictMixin):
    pass

@dataclass
class Event1(Event):
    code: Literal[1] = 1
    ...

@dataclass
class Event2(Event):
    code: Literal[2] = 2
    ...

@dataclass
class Event3(Event):
    code: Literal[3] = 3
    ...

@dataclass
class Message(DataClassDictMixin):
    event: Annotated[
        Union[Event1, Event2],
        Discriminator(field="code", include_supertypes=True),
    ]

event1_msg = Message.from_dict({"event": {"code": 1, ...}})
event2_msg = Message.from_dict({"event": {"code": 2, ...}})
assert isinstance(event1_msg.event, Event1)
assert isinstance(event2_msg.event, Event2)

# raises InvalidFieldValue:
Message.from_dict({"event": {"code": 3, ...}})
```

Again, it's not necessary to have a common superclass. If you have a union of
dataclasses without a field that they can be distinguishable by, you can still
use `Discriminator`, but deserialization will almost be the same as for `Union`
type without `Discriminator` except that it could be possible to deserialize
subclasses with `include_subtypes=True`.

> [!IMPORTANT]\
> When both `include_subtypes` and `include_supertypes` are enabled,
> all subclasses will be attempted to be deserialized first,
> superclasses — at the end.

In the following example you can see how priority works — first we try
to deserialize `ChickpeaHummus`, and if it fails, then we try `Hummus`:

```python
@dataclass
class Hummus(DataClassDictMixin):
    made_of: Literal["chickpeas", "artichoke"]
    grams: int

@dataclass
class ChickpeaHummus(Hummus):
    made_of: Literal["chickpeas"]

@dataclass
class Celery(DataClassDictMixin):
    pieces: int

@dataclass
class Plate(DataClassDictMixin):
    ingredients: List[
        Annotated[
            Union[Hummus, Celery],
            Discriminator(include_subtypes=True, include_supertypes=True),
        ]
    ]

plate = Plate.from_dict(
    {
        "ingredients": [
            {"made_of": "chickpeas", "grams": 100},
            {"made_of": "artichoke", "grams": 50},
            {"pieces": 4},
        ]
    }
)
assert plate == Plate(
    ingredients=[
        ChickpeaHummus(made_of='chickpeas', grams=100),  # <- subclass
        Hummus(made_of='artichoke', grams=50),  # <- superclass
        Celery(pieces=4),
    ]
)
```

#### Using a custom variant tagger function

Sometimes it is impractical to have a class-level attribute with a tag value,
especially when you have a lot of classes. We can have a custom tagger
function instead. This method is applicable for all scenarios of using
the discriminator, but for demonstration purposes, let's focus only on one
of them.

Suppose we want to use the middle part of `Client*Event` as a tag value:

```python
from dataclasses import dataclass
from ipaddress import IPv4Address
from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig
from mashumaro.types import Discriminator


def client_event_tagger(cls):
    # not the best way of doing it, it's just a demo
    return cls.__name__[6:-5].lower()

@dataclass
class ClientEvent(DataClassDictMixin):
    class Config(BaseConfig):
        discriminator = Discriminator(
            field="type",
            include_subtypes=True,
            variant_tagger_fn=client_event_tagger,
        )

@dataclass
class ClientConnectedEvent(ClientEvent):
    client_ip: IPv4Address

@dataclass
class ClientDisconnectedEvent(ClientEvent):
    client_ip: IPv4Address
```

We can now deserialize subclasses as we did it earlier
[without variant tagger](#class-level-discriminator):
```python
disconnected_event = ClientEvent.from_dict(
    {"type": "disconnected", "client_ip": "10.0.0.42"}
)
assert disconnected_event == ClientDisconnectedEvent(IPv4Address("10.0.0.42"))
```

If we need to associate multiple tags with a single variant, we can return
a list of tags:

```python
def client_event_tagger(cls):
    name = cls.__name__[6:-5]
    return [name.lower(), name.upper()]
```

### Code generation options

#### Add `omit_none` keyword argument

If you want to have control over whether to skip `None` values on serialization
you can add `omit_none` parameter to `to_*` methods using the
`code_generation_options` list. The default value of `omit_none`
parameter depends on whether the [`omit_none`](#omit_none-config-option)
config option or [`omit_none`](#omit_none-dialect-option) dialect option is enabled.

```python
from dataclasses import dataclass
from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig, TO_DICT_ADD_OMIT_NONE_FLAG

@dataclass
class Inner(DataClassDictMixin):
    x: int = None
    # "x" won't be omitted since there is no TO_DICT_ADD_OMIT_NONE_FLAG here

@dataclass
class Model(DataClassDictMixin):
    x: Inner
    a: int = None
    b: str = None  # will be omitted

    class Config(BaseConfig):
        code_generation_options = [TO_DICT_ADD_OMIT_NONE_FLAG]

Model(x=Inner(), a=1).to_dict(omit_none=True)  # {'x': {'x': None}, 'a': 1}
```

#### Add `by_alias` keyword argument

If you want to have control over whether to serialize fields by their
[aliases](#field-aliases) you can add `by_alias` parameter to `to_*` methods
using the `code_generation_options` list. The default value of `by_alias`
parameter depends on whether the [`serialize_by_alias`](#serialize_by_alias-config-option)
config option is enabled.

```python
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin, field_options
from mashumaro.config import BaseConfig, TO_DICT_ADD_BY_ALIAS_FLAG

@dataclass
class DataClass(DataClassDictMixin):
    field_a: int = field(metadata=field_options(alias="FieldA"))

    class Config(BaseConfig):
        code_generation_options = [TO_DICT_ADD_BY_ALIAS_FLAG]

DataClass(field_a=1).to_dict()  # {'field_a': 1}
DataClass(field_a=1).to_dict(by_alias=True)  # {'FieldA': 1}
```

#### Add `dialect` keyword argument

Support for [dialects](#dialects) is disabled by default for performance reasons. You can enable
it using a `ADD_DIALECT_SUPPORT` constant:
```python
from dataclasses import dataclass
from datetime import date
from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig, ADD_DIALECT_SUPPORT

@dataclass
class Entity(DataClassDictMixin):
    dt: date

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]
```

#### Add `context` keyword argument

Sometimes it's needed to pass a "context" object to the serialization hooks
that will take it into account. For example, you could want to have an option
to remove sensitive data from the serialization result if you need to.
You can add `context` parameter to `to_*` methods that will be passed to
[`__pre_serialize__`](#before-serialization) and
[`__post_serialize__`](#after-serialization) hooks. The type of this context
as well as its mutability is up to you.

```python
from dataclasses import dataclass
from typing import Dict, Optional
from uuid import UUID
from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig, ADD_SERIALIZATION_CONTEXT

class BaseModel(DataClassDictMixin):
    class Config(BaseConfig):
        code_generation_options = [ADD_SERIALIZATION_CONTEXT]

@dataclass
class Account(BaseModel):
    id: UUID
    username: str
    name: str

    def __pre_serialize__(self, context: Optional[Dict] = None):
        return self

    def __post_serialize__(self, d: Dict, context: Optional[Dict] = None):
        if context and context.get("remove_sensitive_data"):
            d["username"] = "***"
            d["name"] = "***"
        return d

@dataclass
class Session(BaseModel):
    id: UUID
    key: str
    account: Account

    def __pre_serialize__(self, context: Optional[Dict] = None):
        return self

    def __post_serialize__(self, d: Dict, context: Optional[Dict] = None):
        if context and context.get("remove_sensitive_data"):
            d["key"] = "***"
        return d


foo = Session(
    id=UUID('03321c9f-6a97-421e-9869-918ff2867a71'),
    key="VQ6Q9bX4c8s",
    account=Account(
        id=UUID('4ef2baa7-edef-4d6a-b496-71e6d72c58fb'),
        username="john_doe",
        name="John"
    )
)
assert foo.to_dict() == {
    'id': '03321c9f-6a97-421e-9869-918ff2867a71',
    'key': 'VQ6Q9bX4c8s',
    'account': {
        'id': '4ef2baa7-edef-4d6a-b496-71e6d72c58fb',
        'username': 'john_doe',
        'name': 'John'
    }
}
assert foo.to_dict(context={"remove_sensitive_data": True}) == {
    'id': '03321c9f-6a97-421e-9869-918ff2867a71',
    'key': '***',
    'account': {
        'id': '4ef2baa7-edef-4d6a-b496-71e6d72c58fb',
        'username': '***',
        'name': '***'
    }
}
```

### Generic dataclasses

Along with [user-defined generic types](#user-defined-generic-types)
implementing `SerializableType` interface, generic and variadic
generic dataclasses can also be used. There are two applicable scenarios
for them.

#### Generic dataclass inheritance

If you have a generic dataclass and want to serialize and deserialize its
instances depending on the concrete types, you can use inheritance for that:

```python
from dataclasses import dataclass
from datetime import date
from typing import Generic, Mapping, TypeVar, TypeVarTuple
from mashumaro import DataClassDictMixin

KT = TypeVar("KT")
VT = TypeVar("VT", date, str)
Ts = TypeVarTuple("Ts")

@dataclass
class GenericDataClass(Generic[KT, VT, *Ts]):
    x: Mapping[KT, VT]
    y: Tuple[*Ts, KT]

@dataclass
class ConcreteDataClass(
    GenericDataClass[str, date, *Tuple[float, ...]],
    DataClassDictMixin,
):
    pass

ConcreteDataClass.from_dict({"x": {"a": "2021-01-01"}, "y": [1, 2, "a"]})
# ConcreteDataClass(x={'a': datetime.date(2021, 1, 1)}, y=(1.0, 2.0, 'a'))
```

You can override `TypeVar` field with a concrete type or another `TypeVar`.
Partial specification of concrete types is also allowed. If a generic dataclass
is inherited without type overriding the types of its fields remain untouched.

#### Generic dataclass in a field type

Another approach is to specify concrete types in the field type hints. This can
help to have different versions of the same generic dataclass:

```python
from dataclasses import dataclass
from datetime import date
from typing import Generic, TypeVar
from mashumaro import DataClassDictMixin

T = TypeVar('T')

@dataclass
class GenericDataClass(Generic[T], DataClassDictMixin):
    x: T

@dataclass
class DataClass(DataClassDictMixin):
    date: GenericDataClass[date]
    str: GenericDataClass[str]

instance = DataClass(
    date=GenericDataClass(x=date(2021, 1, 1)),
    str=GenericDataClass(x='2021-01-01'),
)
dictionary = {'date': {'x': '2021-01-01'}, 'str': {'x': '2021-01-01'}}
assert DataClass.from_dict(dictionary) == instance
```

### GenericSerializableType interface

There is a generic alternative to [`SerializableType`](#serializabletype-interface)
called `GenericSerializableType`. It makes it possible to decide yourself how
to serialize and deserialize input data depending on the types provided:

```python
from dataclasses import dataclass
from datetime import date
from typing import Dict, TypeVar
from mashumaro import DataClassDictMixin
from mashumaro.types import GenericSerializableType

KT = TypeVar("KT")
VT = TypeVar("VT")

class DictWrapper(Dict[KT, VT], GenericSerializableType):
    __packers__ = {date: lambda x: x.isoformat(), str: str}
    __unpackers__ = {date: date.fromisoformat, str: str}

    def _serialize(self, types) -> Dict[KT, VT]:
        k_type, v_type = types
        k_conv = self.__packers__[k_type]
        v_conv = self.__packers__[v_type]
        return {k_conv(k): v_conv(v) for k, v in self.items()}

    @classmethod
    def _deserialize(cls, value, types) -> "DictWrapper[KT, VT]":
        k_type, v_type = types
        k_conv = cls.__unpackers__[k_type]
        v_conv = cls.__unpackers__[v_type]
        return cls({k_conv(k): v_conv(v) for k, v in value.items()})

@dataclass
class DataClass(DataClassDictMixin):
    x: DictWrapper[date, str]
    y: DictWrapper[str, date]

input_data = {
    "x": {"2022-12-07": "2022-12-07"},
    "y": {"2022-12-07": "2022-12-07"},
}
obj = DataClass.from_dict(input_data)
assert obj == DataClass(
    x=DictWrapper({date(2022, 12, 7): "2022-12-07"}),
    y=DictWrapper({"2022-12-07": date(2022, 12, 7)}),
)
assert obj.to_dict() == input_data
```

As you can see, the code turns out to be massive compared to the
[alternative](#user-defined-generic-types) but in rare cases such flexibility
can be useful. You should think twice about whether it's really worth using it.

### Serialization hooks

In some cases you need to prepare input / output data or do some extraordinary
actions at different stages of the deserialization / serialization lifecycle.
You can do this with different types of hooks.

#### Before deserialization

For doing something with a dictionary that will be passed to deserialization
you can use `__pre_deserialize__` class method:

```python
@dataclass
class A(DataClassJSONMixin):
    abc: int

    @classmethod
    def __pre_deserialize__(cls, d: Dict[Any, Any]) -> Dict[Any, Any]:
        return {k.lower(): v for k, v in d.items()}

print(DataClass.from_dict({"ABC": 123}))    # DataClass(abc=123)
print(DataClass.from_json('{"ABC": 123}'))  # DataClass(abc=123)
```

#### After deserialization

For doing something with a dataclass instance that was created as a result
of deserialization you can use `__post_deserialize__` class method:

```python
@dataclass
class A(DataClassJSONMixin):
    abc: int

    @classmethod
    def __post_deserialize__(cls, obj: 'A') -> 'A':
        obj.abc = 456
        return obj

print(DataClass.from_dict({"abc": 123}))    # DataClass(abc=456)
print(DataClass.from_json('{"abc": 123}'))  # DataClass(abc=456)
```

#### Before serialization

For doing something before serialization you can use `__pre_serialize__`
method:

```python
@dataclass
class A(DataClassJSONMixin):
    abc: int
    counter: ClassVar[int] = 0

    def __pre_serialize__(self) -> 'A':
        self.counter += 1
        return self

obj = DataClass(abc=123)
obj.to_dict()
obj.to_json()
print(obj.counter)  # 2
```

Note that you can add an additional `context` argument using the
[corresponding](#add-context-keyword-argument) code generation option.

#### After serialization

For doing something with a dictionary that was created as a result of
serialization you can use `__post_serialize__` method:

```python
@dataclass
class A(DataClassJSONMixin):
    user: str
    password: str

    def __post_serialize__(self, d: Dict[Any, Any]) -> Dict[Any, Any]:
        d.pop('password')
        return d

obj = DataClass(user="name", password="secret")
print(obj.to_dict())  # {"user": "name"}
print(obj.to_json())  # '{"user": "name"}'
```

Note that you can add an additional `context` argument using the
[corresponding](#add-context-keyword-argument) code generation option.

JSON Schema
-------------------------------------------------------------------------------

You can build JSON Schema not only for dataclasses but also for any other
[supported](#supported-data-types) data
types. There is support for the following standards:
* [Draft 2020-12](https://json-schema.org/specification.html)
* [OpenAPI Specification 3.1.1](https://spec.openapis.org/oas/v3.1.1)

### Building JSON Schema

For simple one-time cases it's recommended to start from using a configurable
`build_json_schema` function. It returns `JSONSchema` object that can be
serialized to json or to dict:

```python
from dataclasses import dataclass, field
from typing import List
from uuid import UUID

from mashumaro.jsonschema import build_json_schema


@dataclass
class User:
    id: UUID
    name: str = field(metadata={"description": "User name"})


print(build_json_schema(List[User]).to_json())
```

<details>
<summary>Click to show the result</summary>

```json
{
    "type": "array",
    "items": {
        "type": "object",
        "title": "User",
        "properties": {
            "id": {
                "type": "string",
                "format": "uuid"
            },
            "name": {
                "type": "string",
                "description": "User name"
            }
        },
        "additionalProperties": false,
        "required": [
            "id",
            "name"
        ]
    }
}
```
</details>

Additional validation keywords ([see below](#json-schema-constraints))
can be added using annotations:

```python
from typing import Annotated, List
from mashumaro.jsonschema import build_json_schema
from mashumaro.jsonschema.annotations import Maximum, MaxItems

print(
    build_json_schema(
        Annotated[
            List[Annotated[int, Maximum(42)]],
            MaxItems(4)
        ]
    ).to_json()
)
```

<details>
<summary>Click to show the result</summary>

```json
{
    "type": "array",
    "items": {
        "type": "integer",
        "maximum": 42
    },
    "maxItems": 4
}
```
</details>

The [`$schema`](https://json-schema.org/draft/2020-12/json-schema-core.html#name-the-schema-keyword)
keyword can be added by setting `with_dialect_uri` to True:

```python
print(build_json_schema(str, with_dialect_uri=True).to_json())
```

<details>
<summary>Click to show the result</summary>

```json
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "string"
}
```
</details>

By default, Draft 2022-12 dialect is being used, but you can change it to
another one by setting `dialect` parameter:

```python
from mashumaro.jsonschema import OPEN_API_3_1

print(
    build_json_schema(
        str, dialect=OPEN_API_3_1, with_dialect_uri=True
    ).to_json()
)
```

<details>
<summary>Click to show the result</summary>

```json
{
    "$schema": "https://spec.openapis.org/oas/3.1/dialect/base",
    "type": "string"
}
```
</details>

All dataclass JSON Schemas can or can not be placed in the
[definitions](https://json-schema.org/draft/2020-12/json-schema-core.html#name-schema-re-use-with-defs)
section, depending on the `all_refs` parameter, which default value comes
from a dialect used (`False` for Draft 2022-12, `True` for OpenAPI
Specification 3.1.1):

```python
print(build_json_schema(List[User], all_refs=True).to_json())
```
<details>
<summary>Click to show the result</summary>

```json
{
    "type": "array",
    "$defs": {
        "User": {
            "type": "object",
            "title": "User",
            "properties": {
                "id": {
                    "type": "string",
                    "format": "uuid"
                },
                "name": {
                    "type": "string"
                }
            },
            "additionalProperties": false,
            "required": [
                "id",
                "name"
            ]
        }
    },
    "items": {
        "$ref": "#/$defs/User"
    }
}
```
</details>

The definitions section can be omitted from the final document by setting
`with_definitions` parameter to `False`:

```python
print(
    build_json_schema(
        List[User], dialect=OPEN_API_3_1, with_definitions=False
    ).to_json()
)
```

<details>
<summary>Click to show the result</summary>

```json
{
    "type": "array",
    "items": {
        "$ref": "#/components/schemas/User"
    }
}
```
</details>

Reference prefix can be changed by using `ref_prefix` parameter:

```python
print(
    build_json_schema(
        List[User],
        all_refs=True,
        with_definitions=False,
        ref_prefix="#/components/responses",
    ).to_json()
)
```

<details>
<summary>Click to show the result</summary>

```json
{
    "type": "array",
    "items": {
        "$ref": "#/components/responses/User"
    }
}
```
</details>

The omitted definitions could be found later in the `Context` object that
you could have created and passed to the function, but it could be easier
to use `JSONSchemaBuilder` for that. For example, you might found it handy
to build OpenAPI Specification step by step passing your models to the builder
and get all the registered definitions later. This builder has reasonable
defaults but can be customized if necessary.

```python
from mashumaro.jsonschema import JSONSchemaBuilder, OPEN_API_3_1

builder = JSONSchemaBuilder(OPEN_API_3_1)

@dataclass
class User:
    id: UUID
    name: str

@dataclass
class Device:
    id: UUID
    model: str

print(builder.build(List[User]).to_json())
print(builder.build(List[Device]).to_json())
print(builder.get_definitions().to_json())
```

<details>
<summary>Click to show the result</summary>

```json
{
    "type": "array",
    "items": {
        "$ref": "#/components/schemas/User"
    }
}
```
```json
{
    "type": "array",
    "items": {
        "$ref": "#/components/schemas/Device"
    }
}
```
```json
{
    "User": {
        "type": "object",
        "title": "User",
        "properties": {
            "id": {
                "type": "string",
                "format": "uuid"
            },
            "name": {
                "type": "string"
            }
        },
        "additionalProperties": false,
        "required": [
            "id",
            "name"
        ]
    },
    "Device": {
        "type": "object",
        "title": "Device",
        "properties": {
            "id": {
                "type": "string",
                "format": "uuid"
            },
            "model": {
                "type": "string"
            }
        },
        "additionalProperties": false,
        "required": [
            "id",
            "model"
        ]
    }
}
```
</details>

### JSON Schema constraints

Apart from required keywords, that are added automatically for certain data
types, you're free to use additional validation keywords.
They're presented by the corresponding classes in
[`mashumaro.jsonschema.annotations`](https://github.com/Fatal1ty/mashumaro/blob/master/mashumaro/jsonschema/annotations.py):

Number constraints:
* [`Minimum`](https://json-schema.org/draft/2020-12/json-schema-validation.html#name-minimum)
* [`Maximum`](https://json-schema.org/draft/2020-12/json-schema-validation.html#name-maximum)
* [`ExclusiveMinimum`](https://json-schema.org/draft/2020-12/json-schema-validation.html#name-exclusiveminimum)
* [`ExclusiveMaximum`](https://json-schema.org/draft/2020-12/json-schema-validation.html#name-exclusivemaximum)
* [`MultipleOf`](https://json-schema.org/draft/2020-12/json-schema-validation.html#name-multipleof)

String constraints:
* [`MinLength`](https://json-schema.org/draft/2020-12/json-schema-validation.html#name-minlength)
* [`MaxLength`](https://json-schema.org/draft/2020-12/json-schema-validation.html#name-maxlength)
* [`Pattern`](https://json-schema.org/draft/2020-12/json-schema-validation.html#name-pattern)

Array constraints:
* [`MinItems`](https://json-schema.org/draft/2020-12/json-schema-validation.html#name-minitems)
* [`MaxItems`](https://json-schema.org/draft/2020-12/json-schema-validation.html#name-maxitems)
* [`UniqueItems`](https://json-schema.org/draft/2020-12/json-schema-validation.html#name-uniqueitems)
* [`Contains`](https://json-schema.org/draft/2020-12/json-schema-core.html#name-contains)
* [`MinContains`](https://json-schema.org/draft/2020-12/json-schema-validation.html#name-mincontains)
* [`MaxContains`](https://json-schema.org/draft/2020-12/json-schema-validation.html#name-maxcontains)

Object constraints:
* [`MaxProperties`](https://json-schema.org/draft/2020-12/json-schema-validation.html#name-maxproperties)
* [`MinProperties`](https://json-schema.org/draft/2020-12/json-schema-validation.html#name-minproperties)
* [`DependentRequired`](https://json-schema.org/draft/2020-12/json-schema-validation.html#name-dependentrequired)

### JSON Schema plugins

If the built-in functionality doesn't meet your needs, you can customize the
JSON Schema generation or add support for additional types using plugins.
The [`mashumaro.jsonschema.plugins.BasePlugin`](https://github.com/Fatal1ty/mashumaro/blob/32179eac1927483f4da015f711b07c04e8b2b2b9/mashumaro/jsonschema/plugins.py#L9-L16)
class provides a `get_schema` method that you can override to implement custom
behavior.

The plugin system works by iterating through all registered plugins and calling
their `get_schema` methods. If a plugin's `get_schema` method raises a
`NotImplementedError` or returns `None`, it indicates that the plugin doesn't
provide the required functionality for that particular case.

You can apply multiple plugins sequentially, allowing each to modify the schema
in turn. This approach enables a step-by-step transformation of the schema,
with each plugin contributing its specific modifications.

Plugins can be registered using the `plugins` argument in either the
`build_json_schema` function or the `JSONSchemaBuilder` class.

The [`mashumaro.jsonschema.plugins`](https://github.com/Fatal1ty/mashumaro/blob/master/mashumaro/jsonschema/plugins.py)
module contains several built-in plugins. Currently, one of these plugins adds
descriptions to JSON schemas using docstrings from dataclasses:

```python
from dataclasses import dataclass

from mashumaro.jsonschema import build_json_schema
from mashumaro.jsonschema.plugins import DocstringDescriptionPlugin


@dataclass
class MyClass:
    """My class"""

    x: int


schema = build_json_schema(MyClass, plugins=[DocstringDescriptionPlugin()])
print(schema.to_json())
```

<details>
<summary>Click to show the result</summary>

```json
{
    "type": "object",
    "title": "MyClass",
    "description": "My class",
    "properties": {
        "x": {
            "type": "integer"
        }
    },
    "additionalProperties": false,
    "required": [
        "x"
    ]
}
```
</details>

Creating your own custom plugin is straightforward. For instance, if you want
to add support for Pydantic models, you could write a plugin similar to the
following:

```python
from dataclasses import dataclass

from pydantic import BaseModel

from mashumaro.jsonschema import build_json_schema
from mashumaro.jsonschema.models import Context, JSONSchema
from mashumaro.jsonschema.plugins import BasePlugin
from mashumaro.jsonschema.schema import Instance


class PydanticSchemaPlugin(BasePlugin):
    def get_schema(
        self,
        instance: Instance,
        ctx: Context,
        schema: JSONSchema | None = None,
    ) -> JSONSchema | None:
        try:
            if issubclass(instance.type, BaseModel):
                pydantic_schema = instance.type.model_json_schema()
                return JSONSchema.from_dict(pydantic_schema)
        except TypeError:
            return None


class MyPydanticClass(BaseModel):
    x: int


@dataclass
class MyDataClass:
    y: MyPydanticClass


schema = build_json_schema(MyDataClass, plugins=[PydanticSchemaPlugin()])
print(schema.to_json())
```

<details>
<summary>Click to show the result</summary>

```json
{
    "type": "object",
    "title": "MyDataClass",
    "properties": {
        "y": {
            "type": "object",
            "title": "MyPydanticClass",
            "properties": {
                "x": {
                    "type": "integer",
                    "title": "X"
                }
            },
            "required": [
                "x"
            ]
        }
    },
    "additionalProperties": false,
    "required": [
        "y"
    ]
}
```
</details>


### Extending JSON Schema

Using a `Config` class it is possible to override some parts of the schema.
Currently, you can do the following:
* override some field schemas using the "properties" key
* change `additionalProperties` using the "additionalProperties" key

```python
from dataclasses import dataclass
from mashumaro.jsonschema import build_json_schema

@dataclass
class FooBar:
    foo: str
    bar: int

    class Config:
        json_schema = {
            "properties": {
                "foo": {
                    "type": "string",
                    "description": "bar"
                }
            },
            "additionalProperties": True,
        }

print(build_json_schema(FooBar).to_json())
```

<details>
<summary>Click to show the result</summary>

```json
{
    "type": "object",
    "title": "FooBar",
    "properties": {
        "foo": {
            "type": "string",
            "description": "bar"
        },
        "bar": {
            "type": "integer"
        }
    },
    "additionalProperties": true,
    "required": [
        "foo",
        "bar"
    ]
}
```
</details>

You can also change the "additionalProperties" key to a specific schema
by passing it a `JSONSchema` instance instead of a bool value.

### JSON Schema and custom serialization methods

Mashumaro provides different ways to override default serialization methods for
dataclass fields or specific data types. In order for these overrides to be
reflected in the schema, you need to make sure that the methods have
annotations of the return value type.

```python
from dataclasses import dataclass, field
from mashumaro.config import BaseConfig
from mashumaro.jsonschema import build_json_schema

def str_as_list(s: str) -> list[str]:
    return list(s)

def int_as_str(i: int) -> str:
    return str(i)

@dataclass
class FooBar:
    foo: str = field(metadata={"serialize": str_as_list})
    bar: int

    class Config(BaseConfig):
        serialization_strategy = {
            int: {
                "serialize": int_as_str
            }
        }

print(build_json_schema(FooBar).to_json())
```

<details>
<summary>Click to show the result</summary>

```json
{
    "type": "object",
    "title": "FooBar",
    "properties": {
        "foo": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "bar": {
            "type": "string"
        }
    },
    "additionalProperties": false,
    "required": [
        "foo",
        "bar"
    ]
}
```
</details>
