from mashumaro.codecs import Decoder, Encoder, decode, encode
from mashumaro.dialect import Dialect
from typing import List
from datetime import date


class MyDialect(Dialect):
    serialization_strategy = {
        date: {
            "serialize": date.toordinal,
            "deserialize": date.fromordinal,
        },
    }


def test_decode():
    assert decode(["2023-09-22", "2023-09-23"], List[date]) == [
        date(2023, 9, 22),
        date(2023, 9, 23),
    ]


def test_encode():
    assert encode([date(2023, 9, 22), date(2023, 9, 23)], List[date]) == [
        "2023-09-22",
        "2023-09-23",
    ]


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
