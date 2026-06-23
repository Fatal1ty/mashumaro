from datetime import date
from typing import Dict, List

import yamlrocks

from mashumaro.codecs.yamlrocks import (
    YAMLRocksDecoder,
    YAMLRocksEncoder,
    yaml_decode,
    yaml_encode,
)
from mashumaro.dialect import Dialect


class MyDialect(Dialect):
    serialization_strategy = {
        date: {"serialize": date.toordinal, "deserialize": date.fromordinal}
    }


def test_yaml_decode():
    data = yamlrocks.dumps(["2023-09-22", "2023-09-23"])
    assert yaml_decode(data, List[date]) == [
        date(2023, 9, 22),
        date(2023, 9, 23),
    ]


def test_yaml_encode():
    assert yaml_encode(
        [date(2023, 9, 22), date(2023, 9, 23)], List[date]
    ) == yamlrocks.dumps([date(2023, 9, 22), date(2023, 9, 23)])


def test_decoder_with_default_dialect():
    decoder = YAMLRocksDecoder(List[date], default_dialect=MyDialect)
    assert decoder.decode(yamlrocks.dumps([738785, 738786])) == [
        date(2023, 9, 22),
        date(2023, 9, 23),
    ]


def test_encoder_with_default_dialect():
    encoder = YAMLRocksEncoder(List[date], default_dialect=MyDialect)
    assert encoder.encode(
        [date(2023, 9, 22), date(2023, 9, 23)]
    ) == yamlrocks.dumps([738785, 738786])


def test_decoder_with_yaml_1_1_via_pre_decoder_func():
    # By default yamlrocks parses YAML 1.2, where "yes" is a string. A custom
    # pre_decoder_func lets callers opt into YAML 1.1, where it is a bool.
    assert yaml_decode("x: yes", Dict[str, str]) == {"x": "yes"}

    decoder = YAMLRocksDecoder(
        Dict[str, bool],
        pre_decoder_func=lambda d: yamlrocks.loads(
            d, option=yamlrocks.OPT_YAML_1_1
        ),
    )
    assert decoder.decode("x: yes") == {"x": True}


def test_encoder_with_post_encoder_func():
    encoder = YAMLRocksEncoder(
        List[int],
        post_encoder_func=lambda obj: yamlrocks.dumps(
            obj, option=yamlrocks.OPT_SORT_KEYS
        ),
    )
    assert encoder.encode([1, 2]) == yamlrocks.dumps(
        [1, 2], option=yamlrocks.OPT_SORT_KEYS
    )
