# mashumaro (マシュマロ)

> **mashumaro** is a fast and well tested serialization framework on top of dataclasses.

[![Build Status](https://travis-ci.org/Fatal1ty/mashumaro.svg?branch=master)](https://travis-ci.org/Fatal1ty/mashumaro)
[![Coverage Status](https://coveralls.io/repos/github/Fatal1ty/mashumaro/badge.svg?branch=master)](https://coveralls.io/github/Fatal1ty/mashumaro?branch=master)
[![Latest Version](https://img.shields.io/pypi/v/mashumaro.svg)](https://pypi.python.org/pypi/mashumaro)
[![Python Version](https://img.shields.io/pypi/pyversions/mashumaro.svg)](https://pypi.python.org/pypi/mashumaro)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


When using dataclasses, you often need to dump and load objects according to
the described scheme.
This framework not only adds this ability to serialize in different formats,
but also makes **serialization rapidly**.

Table of contens
--------------------------------------------------------------------------------
* [Installation](#installation)
* [Supported serialization formats](#supported-serialization-formats)
* [Supported field types](#supported-field-types)
* [Usage example](#usage-example)
* [How does it work?](#how-does-it-work)
* [API](#api)
* [User defined classes](#user-defined-classes)

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

* plain dict
* json
* yaml
* msgpack

Plain dict can be useful when you need to pass a dict object to a
third-party library, such as a client for MongoDB.

Supported field types
--------------------------------------------------------------------------------

There is support for generic types from the standard *typing* module:
* List
* Tuple
* Set
* FrozenSet
* Deque
* Dict
* Mapping
* MutableMapping
* ChainMap
* Sequence

for special primitives from the *typing* module:
* Optional
* Any

for enumerations based on classes from the standard *enum* module:
* Enum
* IntEnum
* Flag
* IntFlag

for common built-in types:
* int
* float
* bool
* str
* bytes
* bytearray

for built-in datetime oriented types:
* datetime
* date
* time
* timedelta

for other less popular built-in types:
* uuid.UUID
* decimal.Decimal
* fractions.Fraction

for specific types like *NoneType*, nested dataclasses itself and
even [user defined classes](#user-defined-classes).


Usage example
--------------------------------------------------------------------------------

```python
from enum import Enum
from typing import Set
from dataclasses import dataclass
from mashumaro import DataClassJSONMixin

class PetType(Enum):
    CAT = 'CAT'
    MOUSE = 'MOUSE'

@dataclass(unsafe_hash=True)
class Pet(DataClassJSONMixin):
    name: str
    age: int
    pet_type: PetType

@dataclass
class Person(DataClassJSONMixin):
    first_name: str
    second_name: str
    age: int
    pets: Set[Pet]


tom = Pet(name='Tom', age=5, pet_type=PetType.CAT)
jerry = Pet(name='Jerry', age=3, pet_type=PetType.MOUSE)
john = Person(first_name='John', second_name='Smith', age=18, pets={tom, jerry})

dump = john.to_json()
person = Person.from_json(dump)
# person == john

Pet.from_json('{"name": "Tom", "age": 5, "pet_type": "CAT"}')
# Pet(name='Tom', age=5, pet_type=<PetType.CAT: 'CAT'>)
```

How does it work?
--------------------------------------------------------------------------------

This framework works by taking the schema of the data and generating a
specific parser and builder for exactly that schema.
This is much faster than inspection of field types on every call of parsing or
building at runtime.

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

User defined classes
--------------------------------------------------------------------------------

You can define and use custom classes with *mashumaro*. There are two options
for customization. The first one is useful when you already have the separate
custom class and you want to serialize instances of it with *mashumaro*.
All what you need is to implement *SerializableType* interface:

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

The second option is useful when you want to change the serialization behaviour
for a class depending on some defined parameters. For this case you can create
the special class implementing *SerializationStrategy* interface:

```python
from datetime import datetime
from dataclasses import dataclass
from mashumaro import DataClassDictMixin
from mashumaro.types import SerializationStrategy

class FormattedDateTime(SerializationStrategy):
    def __init__(self, fmt):
        self.fmt = fmt

    def _serialize(self, value: datetime) -> str:
        return value.strftime(self.fmt)

    def _deserialize(self, value: str) -> datetime:
        return datetime.strptime(value, self.fmt)


@dataclass
class DateTimeFormats(DataClassDictMixin):
    short: FormattedDateTime(fmt='%d%m%Y%H%M%S') = datetime.now()
    verbose: FormattedDateTime(fmt='%A %B %d, %Y, %H:%M:%S') = datetime.now()


formats = DateTimeFormats(
    short=datetime(2019, 1, 1, 12),
    verbose=datetime(2019, 1, 1, 12),
)
dictionary = formats.to_dict()
# {'short': '01012019120000', 'verbose': 'Tuesday January 01, 2019, 12:00:00'}
assert DateTimeFormats.from_dict(dictionary) == formats
```

TODO
--------------------------------------------------------------------------------

* write benchmarks
* add optional validation
* add Union support (try to match types on each call)
* write custom useful types such as URL, Email etc
* write documentation
