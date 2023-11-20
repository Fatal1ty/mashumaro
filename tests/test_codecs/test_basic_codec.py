from dataclasses import dataclass
from datetime import date, datetime
from typing import Generic, List, Optional, TypeVar, Union

import pytest
from typing_extensions import Literal

from mashumaro.codecs import BasicDecoder, BasicEncoder
from mashumaro.codecs.basic import decode, encode
from mashumaro.dialect import Dialect
from tests.entities import (
    DataClassWithoutMixin,
    GenericNamedTuple,
    GenericTypedDict,
    MyGenericDataClass,
)

T = TypeVar("T")


@dataclass
class Foo:
    foo: str


@dataclass
class Bar:
    bar: str


class MyDialect(Dialect):
    serialization_strategy = {
        date: {
            "serialize": date.toordinal,
            "deserialize": date.fromordinal,
        },
    }


@dataclass
class GenericDataClass(Generic[T]):
    x: T
    y: List[T]


@pytest.mark.parametrize(
    ("shape_type", "encoded", "decoded"),
    [
        [
            List[date],
            ["2023-09-22", "2023-09-23"],
            [
                date(2023, 9, 22),
                date(2023, 9, 23),
            ],
        ],
        [DataClassWithoutMixin, {"i": 42}, DataClassWithoutMixin(42)],
        [
            List[DataClassWithoutMixin],
            [{"i": 42}],
            [DataClassWithoutMixin(42)],
        ],
        [
            GenericDataClass,
            {"x": "2023-09-23", "y": ["2023-09-23"]},
            GenericDataClass("2023-09-23", ["2023-09-23"]),
        ],
        [
            GenericDataClass[date],
            {"x": "2023-09-23", "y": ["2023-09-23"]},
            GenericDataClass(date(2023, 9, 23), [date(2023, 9, 23)]),
        ],
        [
            List[Union[int, date]],
            ["42", "2023-09-23"],
            [42, date(2023, 9, 23)],
        ],
        [Optional[date], "2023-09-23", date(2023, 9, 23)],
        [Optional[date], None, None],
    ],
)
def test_decode(shape_type, encoded, decoded):
    assert decode(encoded, shape_type) == decoded


@pytest.mark.parametrize(
    ("shape_type", "encoded", "decoded"),
    [
        [
            List[date],
            ["2023-09-22", "2023-09-23"],
            [
                date(2023, 9, 22),
                date(2023, 9, 23),
            ],
        ],
        [DataClassWithoutMixin, {"i": 42}, DataClassWithoutMixin(42)],
        [
            List[DataClassWithoutMixin],
            [{"i": 42}],
            [DataClassWithoutMixin(42)],
        ],
        [
            GenericDataClass,
            {"x": date(2023, 9, 23), "y": [date(2023, 9, 23)]},
            GenericDataClass(date(2023, 9, 23), [date(2023, 9, 23)]),
        ],
        [
            GenericDataClass[date],
            {"x": "2023-09-23", "y": ["2023-09-23"]},
            GenericDataClass(date(2023, 9, 23), [date(2023, 9, 23)]),
        ],
        [List[Union[int, date]], [42, "2023-09-23"], [42, date(2023, 9, 23)]],
        [Optional[date], "2023-09-23", date(2023, 9, 23)],
        [Optional[date], None, None],
    ],
)
def test_encode(shape_type, encoded, decoded):
    assert encode(decoded, shape_type) == encoded


def test_decoder_with_default_dialect():
    decoder = BasicDecoder(List[date], default_dialect=MyDialect)
    assert decoder.decode([738785, 738786]) == [
        date(2023, 9, 22),
        date(2023, 9, 23),
    ]


def test_encoder_with_default_dialect():
    encoder = BasicEncoder(List[date], default_dialect=MyDialect)
    assert encoder.encode([date(2023, 9, 22), date(2023, 9, 23)]) == [
        738785,
        738786,
    ]


def test_pre_decoder_func():
    decoder = BasicDecoder(List[date], pre_decoder_func=lambda v: v.split(","))
    assert decoder.decode("2023-09-22,2023-09-23") == [
        date(2023, 9, 22),
        date(2023, 9, 23),
    ]


def test_post_encoder_func():
    encoder = BasicEncoder(List[date], post_encoder_func=lambda v: ",".join(v))
    assert (
        encoder.encode(
            [
                date(2023, 9, 22),
                date(2023, 9, 23),
            ]
        )
        == "2023-09-22,2023-09-23"
    )


@pytest.mark.parametrize(
    ("shape_type", "invalid_value"),
    [[Union[date, datetime], "foo"], [Literal["foo"], "bar"]],
)
def test_value_error_on_decode(shape_type, invalid_value):
    decoder = BasicDecoder(shape_type)
    with pytest.raises(ValueError) as e:
        decoder.decode(invalid_value)
    assert type(e.value) is ValueError


@pytest.mark.parametrize(
    ("shape_type", "invalid_value"),
    [[Union[date, datetime], "foo"], [Literal["foo"], "bar"]],
)
def test_value_error_on_encode(shape_type, invalid_value):
    encoder = BasicEncoder(shape_type)
    with pytest.raises(ValueError) as e:
        encoder.encode(invalid_value)
    assert type(e.value) is ValueError


def test_with_fields_with_generated_methods():
    @dataclass
    class MyClass:
        td1: GenericTypedDict[str]
        td2: GenericTypedDict[date]
        nt1: GenericNamedTuple[str]
        nt2: GenericNamedTuple[date]
        u1: List[Union[int, str]]
        u2: List[Union[int, date]]
        l1: Literal["l1"]
        l2: Literal["l2"]

    decoder = BasicDecoder(MyClass)
    encoder = BasicEncoder(MyClass)
    data = {
        "td1": {"x": "2023-11-15", "y": 1},
        "td2": {"x": "2023-11-15", "y": 2},
        "nt1": ["2023-11-15", 3],
        "nt2": ["2023-11-15", 4],
        "u1": [5, "2023-11-15"],
        "u2": [6, "2023-11-15"],
        "l1": "l1",
        "l2": "l2",
    }
    obj = MyClass(
        td1={"x": "2023-11-15", "y": 1},
        td2={"x": date(2023, 11, 15), "y": 2},
        nt1=GenericNamedTuple("2023-11-15", 3),
        nt2=GenericNamedTuple(date(2023, 11, 15), 4),
        u1=[5, "2023-11-15"],
        u2=[6, date(2023, 11, 15)],
        l1="l1",
        l2="l2",
    )
    assert decoder.decode(data) == obj
    assert encoder.encode(obj) == data


def test_with_two_dataclass_fields():
    @dataclass
    class MyClass:
        x1: Foo
        x2: Bar

    decoder = BasicDecoder(MyClass)
    encoder = BasicEncoder(MyClass)
    data = {"x1": {"foo": "foo"}, "x2": {"bar": "bar"}}
    obj = MyClass(x1=Foo("foo"), x2=Bar("bar"))
    assert decoder.decode(data) == obj
    assert encoder.encode(obj) == data


def test_with_two_generic_dataclass_fields():
    @dataclass
    class MyClass:
        x1: MyGenericDataClass[str]
        x2: MyGenericDataClass[date]

    decoder = BasicDecoder(MyClass)
    encoder = BasicEncoder(MyClass)
    data = {"x1": {"x": "2023-11-15"}, "x2": {"x": "2023-11-15"}}
    obj = MyClass(
        x1=MyGenericDataClass("2023-11-15"),
        x2=MyGenericDataClass(date(2023, 11, 15)),
    )
    assert decoder.decode(data) == obj
    assert encoder.encode(obj) == data
