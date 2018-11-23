# mashumaro (マシュマロ)

> **mashumaro** is a fast and well tested serialization framework on top of dataclasses.

[![Build Status](https://travis-ci.org/Fatal1ty/mashumaro.svg?branch=master)](https://travis-ci.org/Fatal1ty/mashumaro)
[![Coverage Status](https://coveralls.io/repos/github/Fatal1ty/mashumaro/badge.svg?branch=master)](https://coveralls.io/github/Fatal1ty/mashumaro?branch=master)
[![Requirements Status](https://requires.io/github/Fatal1ty/mashumaro/requirements.svg?branch=master)](https://requires.io/github/Fatal1ty/mashumaro/requirements/?branch=master)
[![Latest Version](https://img.shields.io/pypi/v/mashumaro.svg)](https://pypi.python.org/pypi/mashumaro)
[![Python Version](https://img.shields.io/pypi/pyversions/mashumaro.svg)](https://pypi.python.org/pypi/mashumaro)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


When using dataclasses, you often need to dump and load objects according to the described scheme.
This framework not only adds this ability to serialize in different formats, but also makes **serialization rapidly**.

Table of contens
--------------------------------------------------------------------------------
* [Installation](#installation)
* [Supported serialization formats](#supported-serialization-formats)
* [Supported field types](#supported-field-types)
* [Usage example](#usage-example)
* [How does it work?](#how-does-it-work)
* [API](#api)

Installation
--------------------------------------------------------------------------------

Use pip to install:
```shell
$ pip install mashumaro
```

Supported serialization formats
--------------------------------------------------------------------------------

This framework adds methods for dumping to and loading from the following formats:

* plain dict
* json
* yaml
* msgpack

Plain dict can be useful when you need to pass a dict object to a third-party library, such as a client for MongoDB.

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

for other specific types like *NoneType* and for nested dataclasses itself.

Usage example
--------------------------------------------------------------------------------

```python
from enum import Enum
from typing import Set
from dataclasses import dataclass
from mashumaro import DataClassJsonMixin

class PetType(Enum):
    CAT = 'CAT'
    MOUSE = 'MOUSE'

@dataclass
class Pet(DataClassJsonMixin):
    name: str
    age: int
    pet_type: PetType

@dataclass
class Person(DataClassJsonMixin):
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

This framework works by taking the schema of the data and generating a specific parser and builder for exactly that schema.
This is much faster than inspection of field types on every call of parsing or building at runtime.

API
--------------------------------------------------------------------------------

Mashumaro provides a couple of mixins for each format.

#### `DataClassJsonMixin.to_json()`

Make a JSON formatted string from dataclass object based on the dataclass schema provided.

#### `DataClassJsonMixin.from_json(data: str)`

Make a new object from JSON formatted string based on the dataclass schema provided.

#### `DataClassMessagePackMixin.to_msgpack()`

Make a MessagePack formatted bytes object from dataclass object based on the dataclass schema provided.

#### `DataClassMessagePackMixin.from_msgpack(data: bytes)`

Make a new object from MessagePack formatted data based on the dataclass schema provided.

#### `DataClassYAMLMixin.to_yaml()`

Make an YAML formatted bytes object from dataclass object based on the dataclass schema provided.

#### `DataClassYAMLMixin.from_yaml(data: bytes)`

Make a new object from YAML formatted data based on the dataclass schema provided.

#### `DataClassDictMixin.to_dict(use_bytes: bool, use_enum: bool, use_datetime: bool)`

Make a dictionary from dataclass object based on the dataclass schema provided. Options include:
```python
use_bytes: false     # False - convert bytes/bytearray objects to base64 encoded string, True - keep untouched
use_enum: false      # False - convert enum objects to enum values, True - keep untouched
use_datetime: false  # False - convert datetime oriented objects to ISO 8601 formatted string, True - keep untouched
```

#### `DataClassDictMixin.from_dict(data: Mapping, use_bytes: bool, use_enum: bool, use_datetime: bool)`

Make a new object from dict object based on the dataclass schema provided. Options include:
```python
use_bytes: false     # False - load bytes/bytearray objects from base64 encoded string, True - keep untouched
use_enum: false      # False - load enum objects from enum values, True - keep untouched
use_datetime: false  # False - load datetime oriented objects from ISO 8601 formatted string, True - keep untouched
```


TODO
--------------------------------------------------------------------------------

* write benchmarks
* add parameters to json serialization methods
* add optional validation
* write custom useful types such as URL, Email etc
* write documentation
