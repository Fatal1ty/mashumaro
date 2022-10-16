from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

import msgpack

from mashumaro import DataClassDictMixin
from mashumaro.config import ADD_DIALECT_SUPPORT, BaseConfig
from mashumaro.dialect import Dialect
from mashumaro.mixins.msgpack import DataClassMessagePackMixin


class MyDialect(Dialect):
    serialization_strategy = {
        bytes: {
            "serialize": lambda x: x.decode(),
            "deserialize": lambda x: x.encode(),
        }
    }


@dataclass
class InnerDataClass(DataClassDictMixin):
    x: bytes


@dataclass
class DataClass(DataClassMessagePackMixin):
    x: bytes
    inner: InnerDataClass


def test_data_class_msgpack_mixin():
    assert DataClassMessagePackMixin.from_msgpack(b"") is None
    assert DataClassMessagePackMixin().to_msgpack() is None


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


def test_msgpack_with_bytes():
    @dataclass
    class DataClass(DataClassMessagePackMixin):
        x: bytes
        y: bytearray

    instance = DataClass(b"123", bytearray(b"456"))
    dumped = msgpack.packb({"x": b"123", "y": bytearray(b"456")})
    assert DataClass.from_msgpack(dumped) == instance
    assert instance.to_msgpack() == dumped


def test_msgpack_with_serialization_strategy():
    @dataclass
    class DataClass(DataClassMessagePackMixin):
        x: bytes

        class Config(BaseConfig):
            serialization_strategy = {
                bytes: {
                    "serialize": lambda x: x.decode(),
                    "deserialize": lambda x: x.encode(),
                }
            }

    instance = DataClass(b"123")
    dumped = msgpack.packb({"x": "123"})
    assert DataClass.from_dict({"x": "123"}) == instance
    assert DataClass.from_msgpack(dumped) == instance
    assert instance.to_dict() == {"x": "123"}
    assert instance.to_msgpack() == dumped


def test_msgpack_with_dialect():
    @dataclass
    class DataClass(DataClassMessagePackMixin):
        x: bytes

        class Config(BaseConfig):
            dialect = MyDialect

    instance = DataClass(b"123")
    dumped_dialect = msgpack.packb({"x": "123"})
    assert DataClass.from_dict({"x": "123"}) == instance
    assert DataClass.from_msgpack(dumped_dialect) == instance
    assert instance.to_dict() == {"x": "123"}
    assert instance.to_msgpack() == dumped_dialect


def test_msgpack_with_dialect_support():
    @dataclass
    class DataClass(DataClassMessagePackMixin):
        x: bytes

        class Config(BaseConfig):
            code_generation_options = [ADD_DIALECT_SUPPORT]

    instance = DataClass(b"123")
    dumped = msgpack.packb({"x": b"123"})
    dumped_dialect = msgpack.packb({"x": "123"})
    assert DataClass.from_dict({"x": "MTIz\n"}) == instance
    assert DataClass.from_dict({"x": "123"}, dialect=MyDialect) == instance
    assert DataClass.from_msgpack(dumped) == instance
    assert (
        DataClass.from_msgpack(dumped_dialect, dialect=MyDialect) == instance
    )
    assert instance.to_dict() == {"x": "MTIz\n"}
    assert instance.to_dict(dialect=MyDialect) == {"x": "123"}
    assert instance.to_msgpack() == dumped
    assert instance.to_msgpack(dialect=MyDialect) == dumped_dialect


def test_msgpack_with_custom_encoder_and_decoder():
    def decoder(data) -> Dict[str, bytes]:
        def to_lower(d):
            result = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    result[k] = to_lower(v)
                else:
                    result[k] = v.lower()
            return result

        return to_lower(msgpack.loads(data))

    def encoder(data: Dict[str, bytes]) -> bytes:
        def to_upper(d):
            result = {}
            for k, v in d.items():
                if isinstance(v, dict):
                    result[k] = to_upper(v)
                else:
                    result[k] = v.upper()
            return result

        return msgpack.dumps(to_upper(data))

    instance = DataClass(b"abc", InnerDataClass(b"def"))
    dumped = msgpack.packb({"x": b"ABC", "inner": {"x": b"DEF"}})
    assert instance.to_msgpack(encoder=encoder) == dumped
    assert DataClass.from_msgpack(dumped, decoder=decoder) == instance
