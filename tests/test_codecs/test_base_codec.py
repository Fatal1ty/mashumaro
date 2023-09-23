from dataclasses import dataclass
from datetime import date, datetime
from typing import Generic, List, Optional, TypeVar, Union

import pytest
from typing_extensions import Literal

from mashumaro.codecs import Decoder, Encoder, decode, encode
from mashumaro.dialect import Dialect
from tests.entities import DataClassWithoutMixin

T = TypeVar("T")


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
    decoder = Decoder(List[date], default_dialect=MyDialect)
    assert decoder.decode([738785, 738786]) == [
        date(2023, 9, 22),
        date(2023, 9, 23),
    ]


def test_encoder_with_default_dialect():
    encoder = Encoder(List[date], default_dialect=MyDialect)
    assert encoder.encode([date(2023, 9, 22), date(2023, 9, 23)]) == [
        738785,
        738786,
    ]


def test_pre_decoder_func():
    decoder = Decoder(List[date], pre_decoder_func=lambda v: v.split(","))
    assert decoder.decode("2023-09-22,2023-09-23") == [
        date(2023, 9, 22),
        date(2023, 9, 23),
    ]


def test_post_encoder_func():
    encoder = Encoder(List[date], post_encoder_func=lambda v: ",".join(v))
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
    decoder = Decoder(shape_type)
    with pytest.raises(ValueError) as e:
        decoder.decode(invalid_value)
    assert type(e.value) is ValueError


@pytest.mark.parametrize(
    ("shape_type", "invalid_value"),
    [[Union[date, datetime], "foo"], [Literal["foo"], "bar"]],
)
def test_value_error_on_encode(shape_type, invalid_value):
    encoder = Encoder(shape_type)
    with pytest.raises(ValueError) as e:
        encoder.encode(invalid_value)
    assert type(e.value) is ValueError
