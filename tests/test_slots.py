from dataclasses import dataclass, field

import pytest

from mashumaro import DataClassDictMixin, field_options
from mashumaro.core.const import PY_310_MIN

if not PY_310_MIN:
    pytest.skip("requires python>=3.10", allow_module_level=True)


def test_field_options_in_dataclass_with_slots():
    @dataclass(slots=True)
    class DataClass(DataClassDictMixin):
        x: int = field(metadata=field_options(serialize=str, alias="alias"))

    instance = DataClass(123)
    assert DataClass.from_dict({"alias": 123}) == instance
    assert instance.to_dict() == {"x": "123"}


def test_field_options_in_inherited_dataclass_with_slots():
    @dataclass
    class BaseDataClass(DataClassDictMixin):
        y: int

    @dataclass(slots=True)
    class DataClass(BaseDataClass):
        x: int = field(metadata=field_options(serialize=str, alias="alias"))

    instance = DataClass(x=123, y=456)
    assert DataClass.from_dict({"alias": 123, "y": 456}) == instance
    assert instance.to_dict() == {"x": "123", "y": 456}


def test_no_field_options_in_inherited_dataclass_with_slots():
    @dataclass
    class BaseDataClass(DataClassDictMixin):
        y: int

    @dataclass(slots=True)
    class DataClass(BaseDataClass):
        x: int

    instance = DataClass(x=123, y=456)
    assert DataClass.from_dict({"x": 123, "y": 456}) == instance
    assert instance.to_dict() == {"x": 123, "y": 456}


def test_no_field_options_in_inherited_dataclass_with_slots_and_default():
    @dataclass
    class BaseDataClass(DataClassDictMixin):
        y: int

    @dataclass(slots=True)
    class DataClass(BaseDataClass):
        x: int = 123

    instance = DataClass(y=456)
    assert DataClass.from_dict({"y": 456}) == instance
    assert instance.to_dict() == {"x": 123, "y": 456}
