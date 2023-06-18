from dataclasses import dataclass
from datetime import date, datetime

from typing_extensions import Annotated

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig


def test_annotated():
    @dataclass
    class DataClass(DataClassDictMixin):
        x: Annotated[date, None]

    obj = DataClass(date(2022, 2, 6))
    assert DataClass.from_dict({"x": "2022-02-06"}) == obj
    assert obj.to_dict() == {"x": "2022-02-06"}


def test_annotated_with_overridden_methods():
    @dataclass
    class DataClass(DataClassDictMixin):
        foo: Annotated[date, "foo"]
        bar: Annotated[date, "bar"]
        baz: Annotated[date, "baz"]

        class Config(BaseConfig):
            serialization_strategy = {
                Annotated[date, "foo"]: {
                    "serialize": date.toordinal,
                    "deserialize": date.fromordinal,
                },
                Annotated[date, "bar"]: {
                    "serialize": date.isoformat,
                    "deserialize": date.fromisoformat,
                },
                date: {
                    "serialize": lambda x: x.strftime("%Y%m%d"),
                    "deserialize": (
                        lambda x: datetime.strptime(x, "%Y%m%d").date()
                    ),
                },
            }

    obj = DataClass(
        foo=date(2023, 6, 12),
        bar=date(2023, 6, 12),
        baz=date(2023, 6, 12),
    )
    obj.foo.strftime("%Y%M%D")
    assert (
        DataClass.from_dict(
            {"foo": 738683, "bar": "2023-06-12", "baz": "20230612"}
        )
        == obj
    )
    assert obj.to_dict() == {
        "foo": 738683,
        "bar": "2023-06-12",
        "baz": "20230612",
    }
