import json
from binascii import hexlify
from dataclasses import dataclass
from datetime import datetime
from typing import List

import pytest

from mashumaro import DataClassJSONMixin, MissingField

from .entities import MyEnum


def test_to_json():
    @dataclass
    class DataClass(DataClassJSONMixin):
        x: List[int]

    dumped = json.dumps({"x": [1, 2, 3]})
    assert DataClass([1, 2, 3]).to_json() == dumped


def test_from_json():
    @dataclass
    class DataClass(DataClassJSONMixin):
        x: List[int]

    dumped = json.dumps({"x": [1, 2, 3]})
    assert DataClass.from_json(dumped) == DataClass([1, 2, 3])


def test_to_json_with_encoder_params():
    @dataclass
    class DataClass(DataClassJSONMixin):
        x: List[int]

    instance = DataClass(x=[1, 2, 3])
    dumped = json.dumps({"x": [1, 2, 3]}, indent=2)
    assert instance.to_json(indent=2) == dumped
    assert instance.to_json() != dumped


def test_to_json_with_custom_encoder():
    @dataclass
    class DataClass(DataClassJSONMixin):
        x: List[int]
        x_count: int

    def encoder(d):
        dd = dict(d)
        dd.pop("x_count", None)
        return json.dumps(dd)

    instance = DataClass(x=[1, 2, 3], x_count=3)
    dumped = json.dumps({"x": [1, 2, 3]})
    assert instance.to_json(encoder=encoder) == dumped
    assert instance.to_json() != dumped


def test_from_json_with_decoder_params():
    @dataclass
    class DataClass(DataClassJSONMixin):
        x: List[float]

    def multiple_by_ten(s):
        return int(s) * 10

    instance = DataClass(x=[10, 20, 30])
    dumped = json.dumps({"x": [1, 2, 3]})
    assert DataClass.from_json(dumped, parse_int=multiple_by_ten) == instance
    assert DataClass.from_json(dumped) != instance


def test_from_json_with_custom_decoder():
    @dataclass
    class DataClass(DataClassJSONMixin):
        x: List[int]
        x_count: int

    def decoder(s):
        d = json.loads(s)
        d["x_count"] = len(d.get("x", []))
        return d

    instance = DataClass(x=[1, 2, 3], x_count=3)
    dumped = json.dumps({"x": [1, 2, 3]})
    assert DataClass.from_json(dumped, decoder=decoder) == instance
    with pytest.raises(MissingField):
        assert DataClass.from_json(dumped)


@pytest.mark.parametrize("use_enum", [True, False])
def test_json_use_enum(use_enum):
    @dataclass
    class DataClass(DataClassJSONMixin):
        x: MyEnum

    def encode_enum(o):
        if isinstance(o, MyEnum):
            return str(o.value).upper()

    def decode_enum(d):
        dd = {}
        for key, value in d.items():
            for enum in MyEnum.__members__.values():
                if value.lower() == enum.value.lower():
                    value = enum
                    break
            dd[key] = value
        return dd

    dumped_with_enum_normal = '{"x": "letter a"}'
    dumped_with_enum_upper = '{"x": "LETTER A"}'

    instance = DataClass(MyEnum.a)

    if not use_enum:
        assert instance.to_json() == dumped_with_enum_normal
        assert (
            instance.to_json(dict_params={"use_enum": False})
            == dumped_with_enum_normal
        )
        assert DataClass.from_json(dumped_with_enum_normal) == instance
        assert (
            DataClass.from_json(
                data=dumped_with_enum_normal, dict_params={"use_enum": False}
            )
            == instance
        )
    else:
        assert (
            instance.to_json(
                default=encode_enum, dict_params={"use_enum": True}
            )
            == dumped_with_enum_upper
        )
        assert (
            DataClass.from_json(
                data=dumped_with_enum_upper,
                object_hook=decode_enum,
                dict_params={"use_enum": True},
            )
            == instance
        )


@pytest.mark.parametrize("use_bytes", [True, False])
def test_json_use_bytes(use_bytes):
    @dataclass
    class DataClass(DataClassJSONMixin):
        x: bytes

    def encode_bytes(o):
        if isinstance(o, bytes):
            return hexlify(o).decode()

    def decode_bytes(d):
        dd = {}
        for key, value in d.items():
            if value == "313233":
                value = b"123"
            dd[key] = value
        return dd

    dumped_with_bytes_normal = r'{"x": "MTIz\n"}'
    dumped_with_bytes_hex = '{"x": "313233"}'

    instance = DataClass(b"123")

    if not use_bytes:
        assert instance.to_json() == dumped_with_bytes_normal
        assert (
            instance.to_json(dict_params={"use_bytes": False})
            == dumped_with_bytes_normal
        )
        assert DataClass.from_json(dumped_with_bytes_normal) == instance
        assert (
            DataClass.from_json(
                data=dumped_with_bytes_normal, dict_params={"use_bytes": False}
            )
            == instance
        )
    else:
        assert (
            instance.to_json(
                default=encode_bytes, dict_params={"use_bytes": True}
            )
            == dumped_with_bytes_hex
        )
        assert (
            DataClass.from_json(
                data=dumped_with_bytes_hex,
                object_hook=decode_bytes,
                dict_params={"use_bytes": True},
            )
            == instance
        )


@pytest.mark.parametrize("use_datetime", [True, False])
def test_json_use_datetime(use_datetime):

    dt = datetime(2018, 10, 29, 12, 46, 55, 308495)

    @dataclass
    class DataClass(DataClassJSONMixin):
        x: datetime

    def encode_datetime(o):
        if isinstance(o, datetime):
            return str(o.timestamp())

    def decode_datetime(d):
        dd = {}
        for key, value in d.items():
            if value == str(dt.timestamp()):
                value = dt
            dd[key] = value
        return dd

    dumped_with_dt_normal = json.dumps({"x": dt.isoformat()})
    dumped_with_dt_timestamp = json.dumps({"x": str(dt.timestamp())})

    instance = DataClass(x=dt)

    if not use_datetime:
        assert instance.to_json() == dumped_with_dt_normal
        assert (
            instance.to_json(dict_params={"use_datetime": False})
            == dumped_with_dt_normal
        )
        assert DataClass.from_json(dumped_with_dt_normal) == instance
        assert (
            DataClass.from_json(
                data=dumped_with_dt_normal, dict_params={"use_datetime": False}
            )
            == instance
        )
    else:
        assert (
            instance.to_json(
                default=encode_datetime, dict_params={"use_datetime": True}
            )
            == dumped_with_dt_timestamp
        )
        assert (
            DataClass.from_json(
                data=dumped_with_dt_timestamp,
                object_hook=decode_datetime,
                dict_params={"use_datetime": True},
            )
            == instance
        )
