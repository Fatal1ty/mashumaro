from datetime import date, datetime, time, timedelta
from dataclasses import dataclass
from decimal import Decimal
from typing import *
from uuid import UUID

import cattr

from benchmark.enums import *


@dataclass
class CATTRSimpleClass:
    int: int
    float: float
    str: str
    bool: bool


@dataclass
class CATTREnumClass:
    enum: MyEnum
    str_enum: MyStrEnum
    int_enum: MyIntEnum
    flag: MyFlag
    int_flag: MyIntFlag


@dataclass
class CATTRDateTimeClass:
    datetime: datetime
    date: date
    time: time
    timedelta: timedelta


@dataclass
class CATTRClass:
    list_simple: List[CATTRSimpleClass]
    list_enum: List[CATTREnumClass]
    tuple_datetime: Tuple[CATTRDateTimeClass, ...]
    dict_complex: Dict[
        int, Mapping[str, MutableMapping[UUID, Sequence[Decimal]]]
    ]


converter = cattr.Converter()

converter.register_structure_hook(
    datetime, lambda s, _: datetime.fromisoformat(s)
)
converter.register_structure_hook(date, lambda s, _: date.fromisoformat(s))
converter.register_structure_hook(time, lambda s, _: time.fromisoformat(s))
converter.register_structure_hook(timedelta, lambda i, _: timedelta(seconds=i))
converter.register_structure_hook(UUID, lambda s, _: UUID(s))
converter.register_structure_hook(Decimal, lambda s, _: Decimal(s))

converter.register_unstructure_hook(datetime, lambda x: x.isoformat())
converter.register_unstructure_hook(date, lambda x: x.isoformat())
converter.register_unstructure_hook(time, lambda x: x.isoformat())
converter.register_unstructure_hook(timedelta, lambda x: x.total_seconds())
converter.register_unstructure_hook(UUID, lambda x: str(x))
converter.register_unstructure_hook(Decimal, lambda x: str(x))
