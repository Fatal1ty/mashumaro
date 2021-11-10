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
* [Supported serialization formats](#supported-serialization-formats)
* [Supported field types](#supported-field-types)
* [Usage example](#usage-example)
* [How does it work?](#how-does-it-work)
* [Benchmark](#benchmark)
* [API](#api)
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
    * [Code generation options](#code-generation-options)
        * [Add `omit_none` keyword argument](#add-omit_none-keyword-argument)
        * [Add `by_alias` keyword argument](#add-by_alias-keyword-argument)
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

Supported serialization formats
--------------------------------------------------------------------------------

This framework adds methods for dumping to and loading from the
following formats:

* [plain dict](https://docs.python.org/3/library/stdtypes.html#mapping-types-dict)
* [JSON](https://www.json.org)
* [YAML](https://yaml.org)
* [MessagePack](https://msgpack.org)

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

for enumerations based on classes from the standard [`enum`](https://docs.python.org/3/library/enum.html) module:
* [`Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)
* [`IntEnum`](https://docs.python.org/3/library/enum.html#enum.IntEnum)
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

for specific types like:
* [`NoneType`](https://docs.python.org/3/library/constants.html#None)
* [user-defined classes](#serializabletype-interface)
* [user-defined generic types](#user-defined-generic-types)

Usage example
--------------------------------------------------------------------------------

```python
from enum import Enum
from typing import List
from dataclasses import dataclass
from mashumaro import DataClassJSONMixin

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
specific parser and builder for exactly that schema.
This is much faster than inspection of field types on every call of parsing or
building at runtime.

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

API
--------------------------------------------------------------------------------

Mashumaro provides a couple of mixins for each format.

#### `DataClassDictMixin.to_dict(use_bytes: bool, use_enum: bool, use_datetime: bool)`

Make a dictionary from dataclass object based on the dataclass schema provided.
Options include:
```python
use_bytes: False     # False - convert bytes/bytearray objects to base64 encoded string, True - keep untouched
use_enum: False      # False - convert enum objects to enum values, True - keep untouched
use_datetime: False  # False - convert datetime oriented objects to ISO 8601 formatted string, True - keep untouched
```

#### `DataClassDictMixin.from_dict(data: Mapping, use_bytes: bool, use_enum: bool, use_datetime: bool)`

Make a new object from dict object based on the dataclass schema provided.
Options include:
```python
use_bytes: False     # False - load bytes/bytearray objects from base64 encoded string, True - keep untouched
use_enum: False      # False - load enum objects from enum values, True - keep untouched
use_datetime: False  # False - load datetime oriented objects from ISO 8601 formatted string, True - keep untouched
```

#### `DataClassJSONMixin.to_json(encoder: Optional[Encoder], dict_params: Optional[Mapping], **encoder_kwargs)`

Make a JSON formatted string from dataclass object based on the dataclass
schema provided. Options include:
```
encoder        # function called for json encoding, defaults to json.dumps
dict_params    # dictionary of parameter values passed underhood to `to_dict` function
encoder_kwargs # keyword arguments for encoder function
```

#### `DataClassJSONMixin.from_json(data: Union[str, bytes, bytearray], decoder: Optional[Decoder], dict_params: Optional[Mapping], **decoder_kwargs)`

Make a new object from JSON formatted string based on the dataclass schema
provided. Options include:
```
decoder        # function called for json decoding, defaults to json.loads
dict_params    # dictionary of parameter values passed underhood to `from_dict` function
decoder_kwargs # keyword arguments for decoder function
```

#### `DataClassMessagePackMixin.to_msgpack(encoder: Optional[Encoder], dict_params: Optional[Mapping], **encoder_kwargs)`

Make a MessagePack formatted bytes object from dataclass object based on the
dataclass schema provided. Options include:
```
encoder        # function called for MessagePack encoding, defaults to msgpack.packb
dict_params    # dictionary of parameter values passed underhood to `to_dict` function
encoder_kwargs # keyword arguments for encoder function
```

#### `DataClassMessagePackMixin.from_msgpack(data: Union[str, bytes, bytearray], decoder: Optional[Decoder], dict_params: Optional[Mapping], **decoder_kwargs)`

Make a new object from MessagePack formatted data based on the
dataclass schema provided. Options include:
```
decoder        # function called for MessagePack decoding, defaults to msgpack.unpackb
dict_params    # dictionary of parameter values passed underhood to `from_dict` function
decoder_kwargs # keyword arguments for decoder function
```

#### `DataClassYAMLMixin.to_yaml(encoder: Optional[Encoder], dict_params: Optional[Mapping], **encoder_kwargs)`

Make an YAML formatted bytes object from dataclass object based on the
dataclass schema provided. Options include:
```
encoder        # function called for YAML encoding, defaults to yaml.dump
dict_params    # dictionary of parameter values passed underhood to `to_dict` function
encoder_kwargs # keyword arguments for encoder function
```

#### `DataClassYAMLMixin.from_yaml(data: Union[str, bytes], decoder: Optional[Decoder], dict_params: Optional[Mapping], **decoder_kwargs)`

Make a new object from YAML formatted data based on the
dataclass schema provided. Options include:
```
decoder        # function called for YAML decoding, defaults to yaml.safe_load
dict_params    # dictionary of parameter values passed underhood to `from_dict` function
decoder_kwargs # keyword arguments for decoder function
```

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

| Applicable field types     | Supported engines        | Description
|:-------------------------- |:-------------------------|:------------------------------|
| `NamedTuple`, `namedtuple` | `as_list`, `as_dict`     | How to pack named tuples. By default `as_list` engine is used that means your named tuple class instance will be packed into a list of its values. You can pack it into a dictionary using `as_dict` engine.

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

| Applicable field types     | Supported engines        | Description
|:-------------------------- |:-------------------------|:------------------------------|
| `datetime`, `date`, `time` | [`ciso8601`](https://github.com/closeio/ciso8601#supported-subset-of-iso-8601), [`pendulum`](https://github.com/sdispater/pendulum) | How to parse datetime string. By default native [`fromisoformat`](https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat) of corresponding class will be used for `datetime`, `date` and `time` fields. It's the fastest way in most cases, but you can choose an alternative. |
| `NamedTuple`, `namedtuple` | `as_list`, `as_dict`     | How to unpack named tuples. By default `as_list` engine is used that means your named tuple class instance will be created from a list of its values. You can unpack it from a dictionary using `as_dict` engine.

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
* [`by_alias` keyword argument in `to_dict` method](#add-by_alias-keyword-argument)

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

| Constant                                                        | Description
|:--------------------------------------------------------------- |:------------------------------------------------------------|
| [`TO_DICT_ADD_OMIT_NONE_FLAG`](#add-omit_none-keyword-argument) | Adds `omit_none` keyword-only argument to `to_dict` method. |
| [`TO_DICT_ADD_BY_ALIAS_FLAG`](#add-by_alias-keyword-argument)   | Adds `by_alias` keyword-only arguments to `to_dict` method. |
| [`PROPAGATE_KWARGS`](#add-propagate_kwargs-option)              | Propagates all kwargs passed to custom serde strategies.    |
| [`LOOSE_DESERIALIZE`](#add-loose_deserialize-option)            | Allows deserializing aliased fields by their true name      |

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

All the fields with [aliases](#alias-option) will be serialized by them when
this option is enabled. The more flexible but less fast way to do the same
is using [`by_alias`](#add-by_alias-keyword-argument) keyword argument.

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
annotations, building of `from_dict` and `to_dict` methods of this dataclass
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

In this case you will get `UnresolvedTypeReferenceError` regardless of whether class B is declared below or not.

### Code generation options

#### Add `omit_none` keyword argument

If you want to have control over whether to skip `None` values on serialization
you can add `omit_none` parameter to `to_dict` method using the
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
[aliases](#alias-option) you can add `by_alias` parameter to `to_dict` method
using the `code_generation_options` list. On the other hand if serialization
by alias is always needed, the best solution is to use the
[`serialize_by_alias`](#serialize_by_alias-config-option) config option.

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

Keep in mind, if you're serializing data in JSON or another format, then you
need to pass `by_alias` argument to [`dict_params`](#dataclassjsonmixinto_jsonencoder-optionalencoder-dict_params-optionalmapping-encoder_kwargs) dictionary.


#### Add `PROPAGATE_KWARGS` Option

When `PROPAGATE_KWARGS` is used in the code generation options, the kwargs
passed to `to_dict` and `from_dict` methods will be propagated to custom
serializers/deserializers.  Use this to create custom serialization dialects
for multiple targets.

```python
class CustomDateSerdeStrategy(SerializationStrategy):

    def serialize(self, value: Arrow, unix: bool = False):
        if unix:
            return int(value.timestamp())
        return value.isoformat()

    def deserialize(self, value):
        return Arrow.get(value)

@dataclass
class DataClass(DataClassDictMixin):
    x: Arrow = field(metadata=field_options(
        serialization_strategy=CustomDateSerdeStrategy()
    ))

    class Config(BaseConfig):
        code_generation_options = [PROPAGATE_KWARGS]

dc = DataClass(x=Arrow(2020, 1, 1))
iso_dict = dc.to_dict()              # {"x": "2020-01-01T00:00:00+00:00"}
unix_dict = dc.to_dict(unix=True)    # {"x": 1577836800}
```

#### Add `LOOSE_DESERIALIZE` Option

When `LOOSE_DESERIALIZE` is used, dict fields matching both the aliased name
as well as the true name may match the field.

```python
@dataclass
class DataClass(DataClassDictMixin):
    x: str = field(metadata=field_options(alias="FieldX"))

    class Config(BaseConfig):
        code_generation_options = [
            LOOSE_DESERIALIZE
        ]

DataClass.from_dict({"FieldX": "Hello"})
DataClass.from_dict({"x": "Hello"})
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
from typing import Dict, TypeVar, Iterator
from datetime import datetime
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
