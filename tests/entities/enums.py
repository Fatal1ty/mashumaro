from enum import Enum, IntEnum, Flag, IntFlag


class MyEnum(Enum):
    a = 'a'
    b = 'b'


class MyIntEnum(IntEnum):
    a = 1
    b = 2


class MyFlag(Flag):
    a = 1
    b = 2


class MyIntFlag(IntFlag):
    a = 1
    b = 2
