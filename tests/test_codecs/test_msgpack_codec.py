from datetime import date
from typing import List

import msgpack

from mashumaro.codecs.msgpack import (
    MessagePackDecoder,
    MessagePackEncoder,
    msgpack_decode,
    msgpack_encode,
)
from mashumaro.dialect import Dialect


class MyDialect(Dialect):
    serialization_strategy = {
        date: {
            "serialize": date.toordinal,
            "deserialize": date.fromordinal,
        },
    }


def test_msgpack_decode():
    data = msgpack.dumps(["2023-09-22", "2023-09-23"])
    assert msgpack_decode(data, List[date]) == [
        date(2023, 9, 22),
        date(2023, 9, 23),
    ]


def test_msgpack_encode():
    data = msgpack.dumps(["2023-09-22", "2023-09-23"])
    assert (
        msgpack_encode([date(2023, 9, 22), date(2023, 9, 23)], List[date])
        == data
    )


def test_decoder_with_default_dialect():
    data = msgpack.dumps([738785, 738786])
    decoder = MessagePackDecoder(List[date], default_dialect=MyDialect)
    assert decoder.decode(data) == [
        date(2023, 9, 22),
        date(2023, 9, 23),
    ]


def test_encoder_with_default_dialect():
    data = msgpack.dumps([738785, 738786])
    encoder = MessagePackEncoder(List[date], default_dialect=MyDialect)
    assert encoder.encode([date(2023, 9, 22), date(2023, 9, 23)]) == data


def test_pre_decoder_func():
    data = msgpack.dumps(["2023-09-22", "2023-09-23"])
    calls = 0

    def pre_decoder_func(value):
        nonlocal calls
        calls += 1
        return msgpack.loads(value)

    decoder = MessagePackDecoder(
        List[date],
        pre_decoder_func=pre_decoder_func,
    )
    assert decoder.decode(data) == [
        date(2023, 9, 22),
        date(2023, 9, 23),
    ]
    assert calls == 1


def test_post_encoder_func():
    data = msgpack.dumps(["2023-09-22", "2023-09-23"])
    calls = 0

    def post_encoder_func(value):
        nonlocal calls
        calls += 1
        return msgpack.dumps(value)

    encoder = MessagePackEncoder(
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
