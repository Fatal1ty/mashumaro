from enum import Enum, Flag, IntEnum, IntFlag


class MyEnum(Enum):
    a = "letter a"
    b = "letter b"


class MyStrEnum(str, Enum):
    a = "letter a"
    b = "letter b"


class MyIntEnum(IntEnum):
    a = 1
    b = 2


class MyFlag(Flag):
    a = 1
    b = 2


class MyIntFlag(IntFlag):
    a = 1
    b = 2
