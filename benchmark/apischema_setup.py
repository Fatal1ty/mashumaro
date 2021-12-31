from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import *
from uuid import UUID

from apischema import (
    PassThroughOptions,
    deserialization_method,
    deserializer,
    serialization_method,
    serializer,
    settings,
)
from apischema.conversions import Conversion, reset_deserializers

from benchmark.enums import *

settings.deserialization.override_dataclass_constructors = True


@dataclass
class APISCHEMASimpleClass:
    int: int
    float: float
    str: str
    bool: bool


@dataclass
class APISCHEMAEnumClass:
    enum: MyEnum
    str_enum: MyStrEnum
    int_enum: MyIntEnum
    flag: MyFlag
    int_flag: MyIntFlag


@dataclass
class APISCHEMADateTimeClass:
    datetime: datetime
    date: date
    time: time
    timedelta: timedelta


@dataclass
class APISCHEMAClass:
    list_simple: List[APISCHEMASimpleClass]
    list_enum: List[APISCHEMAEnumClass]
    tuple_datetime: Tuple[APISCHEMADateTimeClass, ...]
    dict_complex: Dict[
        str, Mapping[str, MutableMapping[UUID, Sequence[Decimal]]]
    ]


@deserializer
def timedelta_from_float(seconds: float) -> timedelta:
    return timedelta(seconds=seconds)


reset_deserializers(Decimal)
deserializer(Conversion(Decimal, source=str))
serializer(Conversion(timedelta.total_seconds, source=timedelta, target=float))

deserialize = deserialization_method(APISCHEMAClass)
serialize = serialization_method(
    APISCHEMAClass, pass_through=PassThroughOptions(collections=True)
)
