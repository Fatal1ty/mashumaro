from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar, Dict, cast

from dateutil.parser import parse

from mashumaro import DataClassDictMixin
from mashumaro.types import SerializableEncoder


class DateTimeSerializableEncoder(SerializableEncoder[datetime]):
    @classmethod
    def _serialize(cls, value: datetime) -> str:
        out = value.isoformat()
        if value.tzinfo is None:
            out = out + "Z"
        return out

    @classmethod
    def _deserialize(cls, value: str) -> datetime:
        return (
            value if isinstance(value, datetime) else parse(cast(str, value))
        )


class MyDataClassDictMixin(DataClassDictMixin):
    _serializable_encoders: ClassVar[Dict[str, SerializableEncoder]] = {
        "datetime.datetime": DateTimeSerializableEncoder(),
    }


def test_ciso8601_datetime_parser():
    @dataclass
    class DataClass(MyDataClassDictMixin):
        generated_at: datetime

    dtnow = datetime.utcnow()
    instance = DataClass(generated_at=dtnow)
    assert instance
    dct = instance.to_dict()
    assert dct["generated_at"] == dtnow.isoformat() + "Z"
