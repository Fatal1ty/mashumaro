from datetime import date
from typing import List

from mashumaro.codecs.orjson import (
    ORJSONDecoder,
    ORJSONEncoder,
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
        == b'["2023-09-22","2023-09-23"]'
    )


def test_decoder_with_default_dialect():
    decoder = ORJSONDecoder(List[date], default_dialect=MyDialect)
    assert decoder.decode("[738785, 738786]") == [
        date(2023, 9, 22),
        date(2023, 9, 23),
    ]


def test_encoder_with_default_dialect():
    encoder = ORJSONEncoder(List[date], default_dialect=MyDialect)
    assert (
        encoder.encode([date(2023, 9, 22), date(2023, 9, 23)])
        == b"[738785,738786]"
    )
