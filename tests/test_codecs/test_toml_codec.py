from datetime import date
from typing import Dict, List

import tomli_w

from mashumaro.codecs.toml import (
    TOMLDecoder,
    TOMLEncoder,
    toml_decode,
    toml_encode,
)
from mashumaro.dialect import Dialect


class MyDialect(Dialect):
    serialization_strategy = {
        date: {
            "serialize": date.toordinal,
            "deserialize": date.fromordinal,
        },
    }


def test_toml_decode():
    data = tomli_w.dumps({"x": [date(2023, 9, 22), date(2023, 9, 23)]})
    assert toml_decode(data, Dict[str, List[date]]) == {
        "x": [
            date(2023, 9, 22),
            date(2023, 9, 23),
        ]
    }


def test_toml_encode():
    data = tomli_w.dumps({"x": [date(2023, 9, 22), date(2023, 9, 23)]})
    assert (
        toml_encode(
            {"x": [date(2023, 9, 22), date(2023, 9, 23)]},
            Dict[str, List[date]],
        )
        == data
    )


def test_decoder_with_default_dialect():
    data = tomli_w.dumps({"x": [738785, 738786]})
    decoder = TOMLDecoder(Dict[str, List[date]], default_dialect=MyDialect)
    assert decoder.decode(data) == {
        "x": [
            date(2023, 9, 22),
            date(2023, 9, 23),
        ]
    }


def test_encoder_with_default_dialect():
    data = tomli_w.dumps({"x": [738785, 738786]})
    encoder = TOMLEncoder(Dict[str, List[date]], default_dialect=MyDialect)
    assert (
        encoder.encode({"x": [date(2023, 9, 22), date(2023, 9, 23)]}) == data
    )
