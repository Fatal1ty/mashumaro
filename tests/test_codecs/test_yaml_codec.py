from datetime import date
from typing import List

import yaml

from mashumaro.codecs.yaml import (
    YAMLDecoder,
    YAMLEncoder,
    yaml_decode,
    yaml_encode,
)
from mashumaro.dialect import Dialect


class MyDialect(Dialect):
    serialization_strategy = {
        date: {
            "serialize": date.toordinal,
            "deserialize": date.fromordinal,
        },
    }


def test_yaml_decode():
    data = "- '2023-09-22'\n- '2023-09-23'\n"
    assert yaml_decode(data, List[date]) == [
        date(2023, 9, 22),
        date(2023, 9, 23),
    ]


def test_yaml_encode():
    data = "- '2023-09-22'\n- '2023-09-23'\n"
    assert (
        yaml_encode([date(2023, 9, 22), date(2023, 9, 23)], List[date]) == data
    )


def test_decoder_with_default_dialect():
    data = "- 738785\n- 738786\n"
    decoder = YAMLDecoder(List[date], default_dialect=MyDialect)
    assert decoder.decode(data) == [
        date(2023, 9, 22),
        date(2023, 9, 23),
    ]


def test_encoder_with_default_dialect():
    data = "- 738785\n- 738786\n"
    encoder = YAMLEncoder(List[date], default_dialect=MyDialect)
    assert encoder.encode([date(2023, 9, 22), date(2023, 9, 23)]) == data


def test_pre_decoder_func():
    data = "- '2023-09-22'\n- '2023-09-23'\n"
    calls = 0

    def pre_decoder_func(value):
        nonlocal calls
        calls += 1
        return yaml.load(value, getattr(yaml, "CSafeLoader", yaml.SafeLoader))

    decoder = YAMLDecoder(
        List[date],
        pre_decoder_func=pre_decoder_func,
    )
    assert decoder.decode(data) == [
        date(2023, 9, 22),
        date(2023, 9, 23),
    ]
    assert calls == 1


def test_post_encoder_func():
    data = "- '2023-09-22'\n- '2023-09-23'\n"
    calls = 0

    def post_encoder_func(value):
        nonlocal calls
        calls += 1
        return yaml.dump(value, Dumper=getattr(yaml, "CDumper", yaml.Dumper))

    encoder = YAMLEncoder(
        List[date],
        post_encoder_func=post_encoder_func,
    )
    assert (
        encoder.encode(
            [
                date(2023, 9, 22),
                date(2023, 9, 23),
            ]
        )
        == data
    )
    assert calls == 1
