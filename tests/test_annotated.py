from dataclasses import dataclass
from datetime import date

from typing_extensions import Annotated

from mashumaro import DataClassDictMixin


def test_annotated():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Annotated[date, None]

    obj = DataClass(date(2022, 2, 6))
    assert DataClass.from_dict({"x": "2022-02-06"}) == obj
    assert obj.to_dict() == {"x": "2022-02-06"}
