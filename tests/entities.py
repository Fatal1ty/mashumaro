from enum import Enum, IntEnum, Flag, IntFlag
from dataclasses import dataclass

from mashumaro import DataClassDictMixin


class MyEnum(Enum):
    a = 'letter a'
    b = 'letter b'


class MyIntEnum(IntEnum):
    a = 1
    b = 2


class MyFlag(Flag):
    a = 1
    b = 2


class MyIntFlag(IntFlag):
    a = 1
    b = 2


@dataclass
class MyDataClass(DataClassDictMixin):
    a: int
    b: int
