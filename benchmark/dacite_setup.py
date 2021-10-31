from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import *
from uuid import UUID

from benchmark.enums import *


@dataclass
class DACITESimpleClass:
    int: int
    float: float
    str: str
    bool: bool


@dataclass
class DACITEEnumClass:
    enum: MyEnum
    str_enum: MyStrEnum
    int_enum: MyIntEnum
    flag: MyFlag
    int_flag: MyIntFlag


@dataclass
class DACITEDateTimeClass:
    datetime: datetime
    date: date
    time: time
    timedelta: timedelta


@dataclass
class DACITEClass:
    list_simple: List[DACITESimpleClass]
    list_enum: List[DACITEEnumClass]
    tuple_datetime: Tuple[DACITEDateTimeClass, ...]
    dict_complex: Dict[
        int, Mapping[str, MutableMapping[UUID, Sequence[Decimal]]]
    ]
