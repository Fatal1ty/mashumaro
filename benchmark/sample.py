import datetime
import random
import uuid
from decimal import Decimal

from benchmark.enums import *

N = 20

sample_1 = {
    "list_simple": [
        {
            "int": 42,
            "float": 3.14,
            "str": "foo bar",
            "bool": True,
        }
        for _ in range(N)
    ],
    "list_enum": [
        {
            "enum": "letter a",
            "str_enum": "letter b",
            "int_enum": 1,
            "flag": 2,
            "int_flag": 1,
        }
        for _ in range(N)
    ],
    "tuple_datetime": [
        {
            "datetime": "2017-01-06T11:16:21.753790",
            "date": "2017-01-06",
            "time": "11:16:21.753790",
            "timedelta": 34234.324234,
        }
        for _ in range(N)
    ],
    "dict_complex": {
        i: {
            str(j): {
                str(uuid.uuid4()): [str(random.random()) for _ in range(N)]
            }
            for j in range(N)
        }
        for i in range(N)
    },
}


sample_2 = {
    "list_simple": [
        {
            "int": 42,
            "float": 3.14,
            "str": "foo bar",
            "bool": True,
        }
        for _ in range(N)
    ],
    "list_enum": [
        {
            "enum": MyEnum.a,
            "str_enum": MyStrEnum.b,
            "int_enum": MyIntEnum.a,
            "flag": MyFlag.b,
            "int_flag": MyIntFlag.a,
        }
        for _ in range(N)
    ],
    "tuple_datetime": (
        {
            "datetime": datetime.datetime(2017, 1, 6, 11, 16, 21, 753790),
            "date": datetime.date(2017, 1, 6),
            "time": datetime.time(11, 16, 21, 753790),
            "timedelta": datetime.timedelta(
                seconds=34234, microseconds=324234
            ),
        }
        for _ in range(N)
    ),
    "dict_complex": {
        i: {
            str(j): {
                uuid.uuid4(): [Decimal(random.random()) for _ in range(N)]
            }
            for j in range(N)
        }
        for i in range(N)
    },
}
