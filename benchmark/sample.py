import datetime
from decimal import Decimal
from uuid import UUID

from benchmark.enums import *

sample_1 = {
    "list_simple": [
        {
            "int": 21745234523,
            "float": 98634.12364812,
            "str": "hello world!",
            "bool": True,
        },
        {
            "int": 86298539432,
            "float": 23423.234923874,
            "str": "foo foo foo",
            "bool": False,
        },
        {
            "int": 2986239423,
            "float": 1123123.1312307,
            "str": "bar bar bar bar",
            "bool": True,
        },
        {
            "int": 776389234,
            "float": 0.2397214222,
            "str": "foo bar baz",
            "bool": False,
        },
        {
            "int": 3331237927323,
            "float": 1.03,
            "str": "foo bar foo bar foo bar foo bar foo bar foo bar",
            "bool": True,
        },
    ],
    "list_enum": [
        {
            "enum": "letter a",
            "str_enum": "letter b",
            "int_enum": 1,
            "flag": 2,
            "int_flag": 1,
        },
        {
            "enum": "letter b",
            "str_enum": "letter a",
            "int_enum": 2,
            "flag": 1,
            "int_flag": 2,
        },
        {
            "enum": "letter a",
            "str_enum": "letter b",
            "int_enum": 1,
            "flag": 2,
            "int_flag": 1,
        },
        {
            "enum": "letter b",
            "str_enum": "letter a",
            "int_enum": 2,
            "flag": 1,
            "int_flag": 2,
        },
        {
            "enum": "letter a",
            "str_enum": "letter b",
            "int_enum": 1,
            "flag": 2,
            "int_flag": 1,
        },
    ],
    "tuple_datetime": [
        {
            "datetime": "2017-01-06T11:16:21.753790",
            "date": "2017-01-06",
            "time": "11:16:21.753790",
            "timedelta": 34234.324234,
        },
        {
            "datetime": "2018-02-07T12:17:22.890532",
            "date": "2018-02-07",
            "time": "12:17:22.890532",
            "timedelta": 4302.388022,
        },
        {
            "datetime": "2019-03-08T13:18:23.890809",
            "date": "2019-03-08",
            "time": "13:18:23.890809",
            "timedelta": 123.14411,
        },
        {
            "datetime": "2020-04-09T14:19:24.832974",
            "date": "2020-04-09",
            "time": "14:19:24.832974",
            "timedelta": 1293.124215,
        },
        {
            "datetime": "2021-05-10T15:20:25.832856",
            "date": "2021-05-10",
            "time": "15:20:25.832856",
            "timedelta": 0.847692,
        },
    ],
    "dict_complex": {
        38632423: {
            "aaa": {
                "ac7e231f-7ea1-43ef-a44a-c6e22ac72a87": [
                    "383.23",
                    "2432.324",
                    "9023.234",
                    "93890.234",
                    "324963.324",
                ],
                "4c1a575a-66a6-4e7e-b747-18069127f31c": [
                    "7634.34",
                    "4813.4862",
                    "99230.373",
                    "384.9634",
                    "567.3934",
                ],
            },
            "bbb": {
                "e38c311d-7037-4e91-a71e-8fb534f5ef5a": [
                    "9374.343",
                    "34.98703",
                    "11.324",
                    "97392.34",
                    "9037.65134",
                ],
                "7a51666c-8229-4101-a127-ee5551363e59": [
                    "386.12",
                    "98023.343",
                    "39001.28764",
                    "5784.24",
                    "47863.36",
                ],
            },
        },
        293691423: {
            "ccc": {
                "e6c55a84-5ffc-4e3e-8659-33765695c103": [
                    "3249.239",
                    "0.996234",
                    "1.23864",
                    "0.9993",
                    "3826423.3451",
                ],
                "9203dfd0-cd64-49da-9c0b-1037d39d77d2": [
                    "3864.234",
                    "8741.0973",
                    "3564.6124",
                    "9034.124",
                    "479.001",
                ],
            },
            "ddd": {
                "60ba3ceb-cb36-4f19-a8e2-86fa99c2fd16": [
                    "386.003",
                    "123.423",
                    "9874.123",
                    "9734.123",
                    "873240.0003",
                ],
                "2ebb9f56-5fed-4da6-b9f1-0982327501c1": [
                    "1240.324",
                    "0.37623423",
                    "88123.92734",
                    "9876.134",
                    "3.45",
                ],
            },
        },
    },
}


sample_2 = {
    "list_simple": [
        {
            "int": 21745234523,
            "float": 98634.12364812,
            "str": "hello world!",
            "bool": True,
        },
        {
            "int": 86298539432,
            "float": 23423.234923874,
            "str": "foo foo foo",
            "bool": False,
        },
        {
            "int": 2986239423,
            "float": 1123123.1312307,
            "str": "bar bar bar bar",
            "bool": True,
        },
        {
            "int": 776389234,
            "float": 0.2397214222,
            "str": "foo bar baz",
            "bool": False,
        },
        {
            "int": 3331237927323,
            "float": 1.03,
            "str": "foo bar foo bar foo bar foo bar foo bar foo bar",
            "bool": True,
        },
    ],
    "list_enum": [
        {
            "enum": MyEnum.a,
            "str_enum": MyStrEnum.b,
            "int_enum": MyIntEnum.a,
            "flag": MyFlag.b,
            "int_flag": MyIntFlag.a,
        },
        {
            "enum": MyEnum.b,
            "str_enum": MyStrEnum.a,
            "int_enum": MyIntEnum.b,
            "flag": MyFlag.a,
            "int_flag": MyIntFlag.b,
        },
        {
            "enum": MyEnum.a,
            "str_enum": MyStrEnum.b,
            "int_enum": MyIntEnum.a,
            "flag": MyFlag.b,
            "int_flag": MyIntFlag.a,
        },
        {
            "enum": MyEnum.b,
            "str_enum": MyStrEnum.a,
            "int_enum": MyIntEnum.b,
            "flag": MyFlag.a,
            "int_flag": MyIntFlag.b,
        },
        {
            "enum": MyEnum.a,
            "str_enum": MyStrEnum.b,
            "int_enum": MyIntEnum.a,
            "flag": MyFlag.b,
            "int_flag": MyIntFlag.a,
        },
    ],
    "tuple_datetime": (
        {
            "datetime": datetime.datetime(2017, 1, 6, 11, 16, 21, 753790),
            "date": datetime.date(2017, 1, 6),
            "time": datetime.time(11, 16, 21, 753790),
            "timedelta": datetime.timedelta(
                seconds=34234, microseconds=324234
            ),
        },
        {
            "datetime": datetime.datetime(2018, 2, 7, 12, 17, 22, 890532),
            "date": datetime.date(2018, 2, 7),
            "time": datetime.time(12, 17, 22, 890532),
            "timedelta": datetime.timedelta(seconds=4302, microseconds=388022),
        },
        {
            "datetime": datetime.datetime(2019, 3, 8, 13, 18, 23, 890809),
            "date": datetime.date(2019, 3, 8),
            "time": datetime.time(13, 18, 23, 890809),
            "timedelta": datetime.timedelta(seconds=123, microseconds=144110),
        },
        {
            "datetime": datetime.datetime(2020, 4, 9, 14, 19, 24, 832974),
            "date": datetime.date(2020, 4, 9),
            "time": datetime.time(14, 19, 24, 832974),
            "timedelta": datetime.timedelta(seconds=1293, microseconds=124215),
        },
        {
            "datetime": datetime.datetime(2021, 5, 10, 15, 20, 25, 832856),
            "date": datetime.date(2021, 5, 10),
            "time": datetime.time(15, 20, 25, 832856),
            "timedelta": datetime.timedelta(microseconds=847692),
        },
    ),
    "dict_complex": {
        38632423: {
            "aaa": {
                UUID("ac7e231f-7ea1-43ef-a44a-c6e22ac72a87"): [
                    Decimal("383.23"),
                    Decimal("2432.324"),
                    Decimal("9023.234"),
                    Decimal("93890.234"),
                    Decimal("324963.324"),
                ],
                UUID("4c1a575a-66a6-4e7e-b747-18069127f31c"): [
                    Decimal("7634.34"),
                    Decimal("4813.4862"),
                    Decimal("99230.373"),
                    Decimal("384.9634"),
                    Decimal("567.3934"),
                ],
            },
            "bbb": {
                UUID("e38c311d-7037-4e91-a71e-8fb534f5ef5a"): [
                    Decimal("9374.343"),
                    Decimal("34.98703"),
                    Decimal("11.324"),
                    Decimal("97392.34"),
                    Decimal("9037.65134"),
                ],
                UUID("7a51666c-8229-4101-a127-ee5551363e59"): [
                    Decimal("386.12"),
                    Decimal("98023.343"),
                    Decimal("39001.28764"),
                    Decimal("5784.24"),
                    Decimal("47863.36"),
                ],
            },
        },
        293691423: {
            "ccc": {
                UUID("e6c55a84-5ffc-4e3e-8659-33765695c103"): [
                    Decimal("3249.239"),
                    Decimal("0.996234"),
                    Decimal("1.23864"),
                    Decimal("0.9993"),
                    Decimal("3826423.3451"),
                ],
                UUID("9203dfd0-cd64-49da-9c0b-1037d39d77d2"): [
                    Decimal("3864.234"),
                    Decimal("8741.0973"),
                    Decimal("3564.6124"),
                    Decimal("9034.124"),
                    Decimal("479.001"),
                ],
            },
            "ddd": {
                UUID("60ba3ceb-cb36-4f19-a8e2-86fa99c2fd16"): [
                    Decimal("386.003"),
                    Decimal("123.423"),
                    Decimal("9874.123"),
                    Decimal("9734.123"),
                    Decimal("873240.0003"),
                ],
                UUID("2ebb9f56-5fed-4da6-b9f1-0982327501c1"): [
                    Decimal("1240.324"),
                    Decimal("0.37623423"),
                    Decimal("88123.92734"),
                    Decimal("9876.134"),
                    Decimal("3.45"),
                ],
            },
        },
    },
}
