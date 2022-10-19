# mashumaro (マシュマロ)

> **mashumaro** is a fast and well tested serialization framework on top of dataclasses.

[![Build Status](https://github.com/Fatal1ty/mashumaro/workflows/tests/badge.svg)](https://github.com/Fatal1ty/mashumaro/actions)
[![Coverage Status](https://coveralls.io/repos/github/Fatal1ty/mashumaro/badge.svg?branch=master)](https://coveralls.io/github/Fatal1ty/mashumaro?branch=master)
[![Latest Version](https://img.shields.io/pypi/v/mashumaro.svg)](https://pypi.python.org/pypi/mashumaro)
[![Python Version](https://img.shields.io/pypi/pyversions/mashumaro.svg)](https://pypi.python.org/pypi/mashumaro)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


When using dataclasses, you often need to dump and load objects according to
the described scheme.
This framework not only adds this ability to serialize in different formats,
but also makes **serialization rapidly**.

Table of contents
--------------------------------------------------------------------------------
* [Installation](#installation)
* [Changelog](#changelog)
* [Supported serialization formats](#supported-serialization-formats)
* [Supported field types](#supported-field-types)
* [Usage example](#usage-example)
* [How does it work?](#how-does-it-work)
* [Benchmark](#benchmark)
* [Serialization mixins](#serialization-mixins)
  * [`DataClassDictMixin`](#dataclassdictmixin)
  * [`DataClassJSONMixin`](#dataclassjsonmixin)
  * [`DataClassORJSONMixin`](#dataclassorjsonmixin)
  * [`DataClassMessagePackMixin`](#dataclassmessagepackmixin)
  * [`DataClassYAMLMixin`](#dataclassyamlmixin)
  * [`DataClassTOMLMixin`](#dataclasstomlmixin)
* [Customization](#customization)
    * [`SerializableType` interface](#serializabletype-interface)
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
        * [`namedtuple_as_dict` config option](#namedtuple_as_dict-config-option)
        * [`allow_postponed_evaluation` config option](#allow_postponed_evaluation-config-option)
        * [`dialect` config option](#dialect-config-option)
        * [`orjson_options`](#orjson_options-config-option)
    * [Passing field values as is](#passing-field-values-as-is)
    * [Dialects](#dialects)
      * [`serialization_strategy` dialect option](#serialization_strategy-dialect-option)
      * [Changing the default dialect](#changing-the-default-dialect)
    * [Code generation options](#code-generation-options)
        * [Add `omit_none` keyword argument](#add-omit_none-keyword-argument)
        * [Add `by_alias` keyword argument](#add-by_alias-keyword-argument)
        * [Add `dialect` keyword argument](#add-dialect-keyword-argument)
    * [User-defined generic types](#user-defined-generic-types)
      * [User-defined generic dataclasses](#user-defined-generic-dataclasses)
      * [Generic dataclasses as field types](#generic-dataclasses-as-field-types)
      * [`GenericSerializableType` interface](#genericserializabletype-interface)
    * [Serialization hooks](#serialization-hooks)
        * [Before deserialization](#before-deserialization)
        * [After deserialization](#after-deserialization)
        * [Before serialization](#before-serialization)
        * [After serialization](#after-serialization)

Installation
--------------------------------------------------------------------------------

Use pip to install:
```shell
$ pip install mashumaro
```

Changelog
--------------------------------------------------------------------------------

This project follows the principles of [Semantic Versioning](https://semver.org).
Changelog is available on [GitHub Releases page](https://github.com/Fatal1ty/mashumaro/releases).

Supported serialization formats
--------------------------------------------------------------------------------

This framework adds methods for dumping to and loading from the
following formats:

* [plain dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)
* [JSON](https://www.json.org)
* [YAML](https://yaml.org)
* [MessagePack](https://msgpack.org)
* [TOML](https://toml.io)

Plain dict can be useful when you need to pass a dict object to a
third-party library, such as a client for MongoDB.

Supported field types
--------------------------------------------------------------------------------

There is support for generic types from the standard [`typing`](https://docs.python.org/3/library/typing.html) module:
* [`List`](https://docs.python.org/3/library/typing.html#typing.List)
* [`Tuple`](https://docs.python.org/3/library/typing.html#typing.Tuple)
* [`NamedTuple`](https://docs.python.org/3/library/typing.html#typing.NamedTuple)
* [`Set`](https://docs.python.org/3/library/typing.html#typing.Set)
* [`FrozenSet`](https://docs.python.org/3/library/typing.html#typing.FrozenSet)
* [`Deque`](https://docs.python.org/3/library/typing.html#typing.Deque)
* [`Dict`](https://docs.python.org/3/library/typing.html#typing.Dict)
* [`OrderedDict`](https://docs.python.org/3/library/typing.html#typing.OrderedDict)
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
* [`NewType`](https://docs.python.org/3/library/typing.html#newtype)
* [`Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated)
* [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal)
* [`Self`](https://docs.python.org/3.11/library/typing.html#typing.Self)

for standard interpreter types from [`types`](https://docs.python.org/3/library/types.html#standard-interpreter-types) module:
* [`NoneType`](https://docs.python.org/3/library/types.html#types.NoneType)
* [`UnionType`](https://docs.python.org/3/library/types.html#types.UnionType)

for enumerations based on classes from the standard [`enum`](https://docs.python.org/3/library/enum.html) module:
* [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)
* [`IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum)
* [`StrEnum`](https://docs.python.org/3.11/library/enum.html#enum.StrEnum)
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

for backported types from [`typing-extensions`](https://github.com/python/typing_extensions):
* [`OrderedDict`](https://docs.python.org/3/library/typing.html#typing.OrderedDict)
* [`TypedDict`](https://docs.python.org/3/library/typing.html#typing.TypedDict)
* [`Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated)
* [`Literal`](https://docs.python.org/3/library/typing.html#typing.Literal)
* [`Self`](https://docs.python.org/3.11/library/typing.html#typing.Self)

for arbitrary types:
* [user-defined classes](#serializabletype-interface)
* [user-defined generic types](#user-defined-generic-types)

Usage example
--------------------------------------------------------------------------------

```python
from enum import Enum
from typing import List
from dataclasses import dataclass
from mashumaro.mixins.json import DataClassJSONMixin

class Currency(Enum):
    USD = "USD"
    EUR = "EUR"

@dataclass
class CurrencyPosition(DataClassJSONMixin):
    currency: Currency
    balance: float

@dataclass
class StockPosition(DataClassJSONMixin):
    ticker: str
    name: str
    balance: int

@dataclass
class Portfolio(DataClassJSONMixin):
    currencies: List[CurrencyPosition]
    stocks: List[StockPosition]

my_portfolio = Portfolio(
    currencies=[
        CurrencyPosition(Currency.USD, 238.67),
        CurrencyPosition(Currency.EUR, 361.84),
    ],
    stocks=[
        StockPosition("AAPL", "Apple", 10),
        StockPosition("AMZN", "Amazon", 10),
    ]
)

json_string = my_portfolio.to_json()
Portfolio.from_json(json_string)  # same as my_portfolio
```

How does it work?
--------------------------------------------------------------------------------

This framework works by taking the schema of the data and generating a
specific parser and builder for exactly that schema, taking into account the
specifics of the serialization format. This is much faster than inspection of
field types on every call of parsing or building at runtime.

These specific parsers and builders are presented by the corresponding
`from_*` and `to_*` methods. They are compiled during import time (or at
runtime in some cases) and are set as attributes to your dataclasses.

Benchmark
--------------------------------------------------------------------------------

* macOS 11.5.2 Big Sur
* Apple M1
* 16GB RAM
* Python 3.9.1

Load and dump [sample data](https://github.com/Fatal1ty/mashumaro/blob/master/benchmark/sample.py) 1.000 times in 5 runs.
The following figures show the best overall time in each case.

<img src="https://raw.githubusercontent.com/Fatal1ty/mashumaro/master/benchmark/charts/load.png" width="400"><img src="https://raw.githubusercontent.com/Fatal1ty/mashumaro/master/benchmark/charts/dump.png" width="400">

<table>
  <col>
  <colgroup span="2"></colgroup>
  <colgroup span="2"></colgroup>
  <tr>
    <th rowspan="2">Framework</th>
    <th colspan="2" scope="colgroup">From dict</th>
    <th colspan="2" scope="colgroup">To dict</th>
</tr>
<tr>
    <th scope="col">Time</th>
    <th scope="col">Slowdown factor</th>
    <th scope="col">Time</th>
    <th scope="col">Slowdown factor</th>
</tr>
<tr>
    <th scope="row"><a href="https://github.com/Fatal1ty/mashumaro">mashumaro</a></th>
    <td align="right">0.04096</td>
    <td align="left">1x</td>
    <td align="right">0.02741</td>
    <td align="left">1x</td>
</tr>
<tr>
    <th scope="row"><a href="https://github.com/Tinche/cattrs">cattrs</a></th>
    <td align="right">0.07307</td>
    <td align="left">1.78x</td>
    <td align="right">0.05062</td>
    <td align="left">1.85x</td>
</tr>
<tr>
    <th scope="row"><a href="https://github.com/samuelcolvin/pydantic/">pydantic</a></th>
    <td align="right">0.24847</td>
    <td align="left">6.07x</td>
    <td align="right">0.12292</td>
    <td align="left">4.48x</td>
</tr>
<tr>
    <th scope="row"><a href="https://github.com/marshmallow-code/marshmallow">marshmallow</a></th>
    <td align="right">0.29205</td>
    <td align="left">7.13x</td>
    <td align="right">0.09310</td>
    <td align="left">3.4x</td>
</tr>
<tr>
    <th scope="row"><a href="https://docs.python.org/3/library/dataclasses.html#dataclasses.asdict">dataclasses</a></th>
    <td align="left">—</td>
    <td align="left">—</td>
    <td align="right">0.22583</td>
    <td align="left">8.24x</td>
</tr>
<tr>
    <th scope="row"><a href="https://github.com/konradhalas/dacite">dacite</a></th>
    <td align="right">0.91553</td>
    <td align="left">22.35x</td>
    <td align="left">—</td>
    <td align="left">—</td>
</tr>
</table>

To run benchmark in your environment:
```bash
git clone git@github.com:Fatal1ty/mashumaro.git
cd mashumaro
python3 -m venv env && source env/bin/activate
pip install -e .
pip install -r requirements-dev.txt
python benchmark/run.py
```

Serialization mixins
--------------------------------------------------------------------------------

Mashumaro provides mixins for each serialization format.

#### [`DataClassDictMixin`](https://github.com/Fatal1ty/mashumaro/blob/master/mashumaro/mixins/dict.py#11)

Can be imported in two ways:
```python
from mashumaro import DataClassDictMixin
from mashumaro.mixins.dict import DataClassDictMixin
```

The core mixin that adds serialization functionality to a dataclass.
This mixin is a base class for all other serialization format mixins.
It adds methods `from_dict` and `to_dict`.

#### [`DataClassJSONMixin`](https://github.com/Fatal1ty/mashumaro/blob/master/mashumaro/mixins/json.py#L14)

Can be imported as:
```python
from mashumaro.mixins.json import DataClassJSONMixin
```

This mixins adds json serialization functionality to a dataclass.
It adds methods `from_json` and `to_json`.

#### [`DataClassORJSONMixin`](https://github.com/Fatal1ty/mashumaro/blob/master/mashumaro/mixins/orjson.py#L29)

Can be imported as:
```python
from mashumaro.mixins.orjson import DataClassORJSONMixin
```

This mixins adds json serialization functionality to a dataclass using
a third-party [`orjson`](https://pypi.org/project/orjson/) library.
It adds methods `from_json`, `to_jsonb`, `to_json`.

In order to use this mixin, the [`orjson`](https://pypi.org/project/orjson/) package must be installed.
You can install it manually or using an extra option for mashumaro:

```shell
pip install mashumaro[orjson]
```

Using this mixin the following data types will be handled by
[`orjson`](https://pypi.org/project/orjson/) library by default:
* [`datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime)
* [`date`](https://docs.python.org/3/library/datetime.html#datetime.date)
* [`time`](https://docs.python.org/3/library/datetime.html#datetime.time)
* [`uuid.UUID`](https://docs.python.org/3/library/uuid.html#uuid.UUID)

#### [`DataClassMessagePackMixin`](https://github.com/Fatal1ty/mashumaro/blob/master/mashumaro/mixins/msgpack.py#L35)

Can be imported as:
```python
from mashumaro.mixins.msgpack import DataClassMessagePackMixin
```

This mixins adds MessagePack serialization functionality to a dataclass.
It adds methods `from_msgpack` and `to_msgpack`.

In order to use this mixin, the [`msgpack`](https://pypi.org/project/msgpack/) package must be installed.
You can install it manually or using an extra option for mashumaro:

```shell
pip install mashumaro[msgpack]
```

Using this mixin the following data types will be handled by
[`msgpack`](https://pypi.org/project/msgpack/) library by default:
* [`bytes`](https://docs.python.org/3/library/stdtypes.html#bytes)
* [`bytearray`](https://docs.python.org/3/library/stdtypes.html#bytearray)

#### [`DataClassYAMLMixin`](https://github.com/Fatal1ty/mashumaro/blob/master/mashumaro/mixins/yaml.py#L27)

Can be imported as:
```python
from mashumaro.mixins.yaml import DataClassYAMLMixin
```

This mixins adds YAML serialization functionality to a dataclass.
It adds methods `from_yaml` and `to_yaml`.

In order to use this mixin, the [`pyyaml`](https://pypi.org/project/PyYAML/) package must be installed.
You can install it manually or using an extra option for mashumaro:

```shell
pip install mashumaro[yaml]
```

#### [`DataClassTOMLMixin`](https://github.com/Fatal1ty/mashumaro/blob/master/mashumaro/mixins/toml.py#L31)

Can be imported as:
```python
from mashumaro.mixins.toml import DataClassTOMLMixin
```

This mixins adds TOML serialization functionality to a dataclass.
It adds methods `from_toml` and `to_toml`.

In order to use this mixin, the [`tomli`](https://pypi.org/project/tomli/) and
[`tomli-w`](https://pypi.org/project/tomli-w/) packages must be installed.
In Python 3.11+, `tomli` is included as
[`tomlib`](https://docs.python.org/3.11/library/tomllib.html) standard library
module and can be used my this mixin.
You can install the missing packages manually or using an extra option for mashumaro:

```shell
pip install mashumaro[toml]
```

Using this mixin the following data types will be handled by
[`tomli`](https://pypi.org/project/tomli/)/
[`tomli-w`](https://pypi.org/project/tomli-w/) library by default:
* [`datetime`](https://docs.python.org/3/library/datetime.html#datetime.datetime)
* [`date`](https://docs.python.org/3/library/datetime.html#datetime.date)
* [`time`](https://docs.python.org/3/library/datetime.html#datetime.time)

Customization
--------------------------------------------------------------------------------

### SerializableType interface

If you already have a separate custom class, and you want to serialize
instances of it with *mashumaro*, you can achieve this by implementing
`SerializableType` interface:

```python
from typing import Dict
from datetime import datetime
from dataclasses import dataclass
from mashumaro import DataClassDictMixin
from mashumaro.types import SerializableType

class DateTime(datetime, SerializableType):
    def _serialize(self) -> Dict[str, int]:
        return {
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "second": self.second,
        }

    @classmethod
    def _deserialize(cls, value: Dict[str, int]) -> 'DateTime':
        return DateTime(
            year=value['year'],
            month=value['month'],
            day=value['day'],
            hour=value['hour'],
            minute=value['minute'],
            second=value['second'],
        )


@dataclass
class Holiday(DataClassDictMixin):
    when: DateTime = DateTime.now()


new_year = Holiday(when=DateTime(2019, 1, 1, 12))
dictionary = new_year.to_dict()
# {'x': {'year': 2019, 'month': 1, 'day': 1, 'hour': 0, 'minute': 0, 'second': 0}}
assert Holiday.from_dict(dictionary) == new_year
```

If you have a custom [generic type](https://docs.python.org/3/library/typing.html#user-defined-generic-types)
and are looking for a generic version of such an interface, read [this](#genericserializabletype-interface).

### Field options

In some cases creating a new class just for one little thing could be
excessive. Moreover, you may need to deal with third party classes that you are
not allowed to change. You can use[`dataclasses.field`](https://docs.python.org/3/library/dataclasses.html#dataclasses.field)
function as a default field value to configure some serialization aspects
through its `metadata` parameter. Next section describes all supported options
to use in `metadata` mapping.

#### `serialize` option

This option allows you to change the serialization method. When using
this option, the serialization behaviour depends on what type of value the
option has. It could be either `Callable[[Any], Any]` or `str`.

A value of type `Callable[[Any], Any]` is a generic way to specify any callable
object like a function, a class method, a class instance method, an instance
of a callable class or even a lambda function to be called for serialization.

A value of type `str` sets a specific engine for serialization. Keep in mind
that all possible engines depend on the field type that this option is used
with. At this moment there are next serialization engines to choose from:

| Applicable field types     | Supported engines        | Description                                                                                                                                                                                                  |
|:-------------------------- |:-------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `NamedTuple`, `namedtuple` | `as_list`, `as_dict`     | How to pack named tuples. By default `as_list` engine is used that means your named tuple class instance will be packed into a list of its values. You can pack it into a dictionary using `as_dict` engine. |

In addition, you can pass a field value as is without changes using
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
that all possible engines depend on the field type that this option is used
with. At this moment there are next deserialization engines to choose from:

| Applicable field types     | Supported engines                                                                                                                   | Description                                                                                                                                                                                                                                                                                             |
|:---------------------------|:------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `datetime`, `date`, `time` | [`ciso8601`](https://github.com/closeio/ciso8601#supported-subset-of-iso-8601), [`pendulum`](https://github.com/sdispater/pendulum) | How to parse datetime string. By default native [`fromisoformat`](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat) of corresponding class will be used for `datetime`, `date` and `time` fields. It's the fastest way in most cases, but you can choose an alternative. |
| `NamedTuple`, `namedtuple` | `as_list`, `as_dict`                                                                                                                | How to unpack named tuples. By default `as_list` engine is used that means your named tuple class instance will be created from a list of its values. You can unpack it from a dictionary using `as_dict` engine.                                                                                       |

In addition, you can pass a field value as is without changes using
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

This option is useful when you want to change the serialization behaviour
for a class depending on some defined parameters. For this case you can create
the special class implementing `SerializationStrategy` interface:

```python
from dataclasses import dataclass, field
from datetime import datetime
from mashumaro import DataClassDictMixin
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
        metadata={
            "serialization_strategy": FormattedDateTime(
                fmt="%d%m%Y%H%M%S",
            )
        }
    )
    verbose: datetime = field(
        metadata={
            "serialization_strategy": FormattedDateTime(
                fmt="%A %B %d, %Y, %H:%M:%S",
            )
        }
    )

formats = DateTimeFormats(
    short=datetime(2019, 1, 1, 12),
    verbose=datetime(2019, 1, 1, 12),
)
dictionary = formats.to_dict()
# {'short': '01012019120000', 'verbose': 'Tuesday January 01, 2019, 12:00:00'}
assert DateTimeFormats.from_dict(dictionary) == formats
```

In addition, you can pass a field value as is without changes using
[`pass_through`](#passing-field-values-as-is).

#### `alias` option

In some cases it's better to have different names for a field in your class and
in its serialized view. For example, a third-party legacy API you are working
with might operate with camel case style, but you stick to snake case style in
your code base. Or even you want to load data with keys that are invalid
identifiers in Python. This problem is easily solved by using aliases:

```python
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin, field_options

@dataclass
class DataClass(DataClassDictMixin):
    a: int = field(metadata=field_options(alias="FieldA"))
    b: int = field(metadata=field_options(alias="#invalid"))

x = DataClass.from_dict({"FieldA": 1, "#invalid": 2})  # DataClass(a=1, b=2)
x.to_dict()  # {"a": 1, "b": 2}  # no aliases on serialization by default
```

If you want to write all the field aliases in one place there is
[such a config option](#aliases-config-option).

If you want to serialize all the fields by aliases you have two options to do so:
* [`serialize_by_alias` config option](#serialize_by_alias-config-option)
* [`by_alias` keyword argument in `to_*` methods](#add-by_alias-keyword-argument)

It's hard to imagine when it might be necessary to serialize only specific
fields by alias, but such functionality is easily added to the library. Open
the issue if you need it.

If you don't want to remember the names of the options you can use
`field_options` helper function:

```python
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin, field_options

@dataclass
class A(DataClassDictMixin):
    x: int = field(
        metadata=field_options(
            serialize=str,
            deserialize=int,
            ...
        )
    )
```

More options are on the way. If you know which option would be useful for many,
please don't hesitate to create an issue or pull request.

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

#### `serialization_strategy` config option

You can register custom `SerializationStrategy`, `serialize` and `deserialize`
methods for specific types just in one place. It could be configured using
a dictionary with types as keys. The value could be either a
`SerializationStrategy` instance or a dictionary with `serialize` and
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

    datetime: datetime
    date: date

    class Config(BaseConfig):
        serialization_strategy = {
            datetime: FormattedDateTime("%Y"),
            date: {
                # you can use specific str values for datetime here as well
                "deserialize": "pendulum",
                "serialize": date.isoformat,
            },
        }

instance = DataClass.from_dict({"datetime": "2021", "date": "2021"})
# DataClass(datetime=datetime.datetime(2021, 1, 1, 0, 0), date=Date(2021, 1, 1))
dictionary = instance.to_dict()
# {'datetime': '2021', 'date': '2021-01-01'}
```

#### `aliases` config option

Sometimes it's better to write the field aliases in one place. You can mix
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

All the fields with [aliases](#alias-option) will be serialized by them by
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

### Passing field values as is

In some cases it's needed to pass a field value as is without any changes
during serialization / deserialization. There is a predefined
[`pass_through`](https://github.com/Fatal1ty/mashumaro/blob/master/mashumaro/helper.py#L46)
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

### Dialects

Sometimes it's needed to have different serialization and deserialization
methods depending on the data source where entities of the dataclass are
stored or on the API to which the entities are being sent or received from.
There is a special Dialect type that may contain all the differences from the
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
but for the dialect scope. You can register custom `SerializationStrategy`,
`serialize` and `deserialize` methods for specific types.

#### Changing the default dialect

You can change the default serialization and deserialization methods for
a dataclass not only in the
[`serialization_strategy`](#serialization_strategy-config-option) config option
but using the `dialect` config option. If you have multiple dataclasses without
a common parent class the default dialect can help you to reduce the number of
code lines written:

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

### Code generation options

#### Add `omit_none` keyword argument

If you want to have control over whether to skip `None` values on serialization
you can add `omit_none` parameter to `to_*` methods using the
`code_generation_options` list:

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
[aliases](#alias-option) you can add `by_alias` parameter to `to_*` methods
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

### User-defined generic types

There is support for [user-defined generic types](https://docs.python.org/3/library/typing.html#user-defined-generic-types).
You can inherit generic dataclasses along with overwriting types in them, use generic
dataclasses as field types, or create your own generic types with serialization
under your control.

#### User-defined generic dataclasses

If you have a generic version of a dataclass and want to serialize and
deserialize its instances depending on the concrete types, you can achieve
this using inheritance:

```python
from dataclasses import dataclass
from datetime import date
from typing import Generic, Mapping, TypeVar
from mashumaro import DataClassDictMixin

KT = TypeVar("KT")
VT = TypeVar("VT", date, str)

@dataclass
class GenericDataClass(Generic[KT, VT]):
    x: Mapping[KT, VT]

@dataclass
class ConcreteDataClass(GenericDataClass[str, date], DataClassDictMixin):
    pass

ConcreteDataClass.from_dict({"x": {"a": "2021-01-01"}})          # ok
ConcreteDataClass.from_dict({"x": {"a": "not a date but str"}})  # error
```

You can override `TypeVar` field with a concrete type or another `TypeVar`.
Partial specification of concrete types is also allowed. If a generic dataclass
is inherited without type overriding the types of its fields remain untouched.

#### Generic dataclasses as field types

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

#### GenericSerializableType interface

There is a generic alternative to [`SerializableType`](#serializabletype-interface)
called `GenericSerializableType`. It makes it possible to serialize and deserialize
instances of generic types depending on the types provided:

```python
from typing import Dict, TypeVar
from dataclasses import dataclass
from mashumaro import DataClassDictMixin
from mashumaro.types import GenericSerializableType

KT = TypeVar("KT", int, str)
VT = TypeVar("VT", int, str)

class GenericDict(Dict[KT, VT], GenericSerializableType):
    def _serialize(self, types) -> Dict[KT, VT]:
        k_type, v_type = types
        if k_type not in (int, str) or v_type not in (int, str):
            raise TypeError
        return {k_type(k): v_type(v) for k, v in self.items()}

    @classmethod
    def _deserialize(cls, value, types) -> 'GenericDict[KT, VT]':
        k_type, v_type = types
        if k_type not in (int, str) or v_type not in (int, str):
            raise TypeError
        return cls({k_type(k): v_type(v) for k, v in value.items()})

@dataclass
class DataClass(DataClassDictMixin):
    x: GenericDict[int, str]
    y: GenericDict[str, int]

instance = DataClass(GenericDict({1: 'a'}), GenericDict({'b': 2}))
dictionary = instance.to_dict()  # {'x': {1: 'a'}, 'y': {'b': 2}}
assert DataClass.from_dict(dictionary) == instance
```

The difference between [`SerializableType`](#serializabletype-interface) and
[`GenericSerializableType`](#genericserializabletype-interface) is that
the methods of [`GenericSerializableType`](#genericserializabletype-interface)
have a parameter `types`, to which the concrete types will be passed.
If you don't need this information you can still use
[`SerializableType`](#serializabletype-interface) interface even with generic
types.

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

TODO
--------------------------------------------------------------------------------

* add optional validation
* write custom useful types such as URL, Email etc
