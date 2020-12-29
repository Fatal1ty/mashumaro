from dataclasses import dataclass
from datetime import datetime
from typing import List

import msgpack

from mashumaro import DataClassMessagePackMixin


def test_to_msgpack():
    @dataclass
    class DataClass(DataClassMessagePackMixin):
        x: List[int]

    dumped = msgpack.packb({"x": [1, 2, 3]})
    assert DataClass([1, 2, 3]).to_msgpack() == dumped


def test_from_msgpack():
    @dataclass
    class DataClass(DataClassMessagePackMixin):
        x: List[int]

    dumped = msgpack.packb({"x": [1, 2, 3]})
    assert DataClass.from_msgpack(dumped) == DataClass([1, 2, 3])


def test_to_msg_pack_datetime():
    @dataclass
    class DataClass(DataClassMessagePackMixin):
        x: datetime

    dt = datetime(2018, 10, 29, 12, 46, 55, 308495)
    dumped = msgpack.packb({"x": dt.isoformat()})
    assert DataClass(dt).to_msgpack() == dumped
