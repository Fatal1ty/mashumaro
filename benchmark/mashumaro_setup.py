from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import *
from uuid import UUID

from benchmark.enums import *
from mashumaro import DataClassDictMixin


@dataclass
class MASHUMAROSimpleClass(DataClassDictMixin):
    int: int
    float: float
    str: str
    bool: bool


@dataclass
class MASHUMAROEnumClass(DataClassDictMixin):
    enum: MyEnum
    str_enum: MyStrEnum
    int_enum: MyIntEnum
    flag: MyFlag
    int_flag: MyIntFlag


@dataclass
class MASHUMARODateTimeClass(DataClassDictMixin):
    datetime: datetime
    date: date
    time: time
    timedelta: timedelta


@dataclass
class MASHUMAROClass(DataClassDictMixin):
    list_simple: List[MASHUMAROSimpleClass]
    list_enum: List[MASHUMAROEnumClass]
    tuple_datetime: Tuple[MASHUMARODateTimeClass, ...]
    dict_complex: Dict[
        int, Mapping[str, MutableMapping[UUID, Sequence[Decimal]]]
    ]
