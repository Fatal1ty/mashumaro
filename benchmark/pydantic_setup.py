from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import *
from uuid import UUID

import pydantic

from benchmark.enums import *


class PYDANTICSimpleClass(pydantic.BaseModel):
    int: int
    float: float
    str: str
    bool: bool


class PYDANTICEnumClass(pydantic.BaseModel):
    enum: MyEnum
    str_enum: MyStrEnum
    int_enum: MyIntEnum
    flag: MyFlag
    int_flag: MyIntFlag


class PYDANTICDateTimeClass(pydantic.BaseModel):
    datetime: datetime
    date: date
    time: time
    timedelta: timedelta


class PYDANTICClass(pydantic.BaseModel):
    list_simple: List[PYDANTICSimpleClass]
    list_enum: List[PYDANTICEnumClass]
    tuple_datetime: Tuple[PYDANTICDateTimeClass, ...]
    dict_complex: Dict[
        int, Mapping[str, MutableMapping[UUID, Sequence[Decimal]]]
    ]
