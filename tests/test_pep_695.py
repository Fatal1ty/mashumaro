from dataclasses import dataclass
from datetime import date

from mashumaro import DataClassDictMixin
from mashumaro.codecs import BasicDecoder, BasicEncoder


def test_type_alias_type_with_dataclass_dict_mixin():
    type MyDate = date

    @dataclass
    class MyClass(DataClassDictMixin):
        x: MyDate

    obj = MyClass(date(2024, 4, 15))
    assert MyClass.from_dict({"x": "2024-04-15"}) == obj
    assert obj.to_dict() == {"x": "2024-04-15"}


def test_type_alias_type_with_codecs():
    type MyDate = date
    decoder = BasicDecoder(MyDate)
    encoder = BasicEncoder(MyDate)

    obj = date(2024, 4, 15)
    assert decoder.decode("2024-04-15") == obj
    assert encoder.encode(obj) == "2024-04-15"
