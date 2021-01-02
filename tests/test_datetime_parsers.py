from dataclasses import dataclass, field
from datetime import datetime, timezone
from mashumaro import DataClassDictMixin


def test_ciso8601_parser():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: datetime = field(metadata={"engine": "ciso8601"})

    assert DataClass.from_dict({"x": "2021-01-02T07:00:00Z"}) == DataClass(
        x=datetime(2021, 1, 2, 7, tzinfo=timezone.utc)
    )
