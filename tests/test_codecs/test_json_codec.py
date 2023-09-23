import json
from datetime import date
from typing import List

from mashumaro.codecs.json import (
    JSONDecoder,
    JSONEncoder,
    json_decode,
    json_encode,
)
from mashumaro.dialect import Dialect


class MyDialect(Dialect):
    serialization_strategy = {
        date: {
            "serialize": date.toordinal,
            "deserialize": date.fromordinal,
        },
    }


def test_json_decode():
    assert json_decode('["2023-09-22", "2023-09-23"]', List[date]) == [
        date(2023, 9, 22),
        date(2023, 9, 23),
    ]


def test_json_encode():
    assert (
        json_encode([date(2023, 9, 22), date(2023, 9, 23)], List[date])
        == '["2023-09-22", "2023-09-23"]'
    )


def test_decoder_with_default_dialect():
    decoder = JSONDecoder(List[date], default_dialect=MyDialect)
    assert decoder.decode("[738785, 738786]") == [
        date(2023, 9, 22),
        date(2023, 9, 23),
    ]


def test_encoder_with_default_dialect():
    encoder = JSONEncoder(List[date], default_dialect=MyDialect)
    assert (
        encoder.encode([date(2023, 9, 22), date(2023, 9, 23)])
        == "[738785, 738786]"
    )


def test_pre_decoder_func():
    decoder = JSONDecoder(
        List[date],
        pre_decoder_func=lambda v: json.loads(
            "[" + ",".join(f'"{v}"' for v in v.split(",")) + "]"
        ),
    )
    assert decoder.decode("2023-09-22,2023-09-23") == [
        date(2023, 9, 22),
        date(2023, 9, 23),
    ]


def test_post_encoder_func():
    encoder = JSONEncoder(
        List[date],
        post_encoder_func=lambda v: json.dumps(v, separators=(",", ":")),
    )
    assert (
        encoder.encode(
            [
                date(2023, 9, 22),
                date(2023, 9, 23),
            ]
        )
        == '["2023-09-22","2023-09-23"]'
    )
