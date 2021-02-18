from dataclasses import dataclass, field
from typing import Optional, Union

from mashumaro import DataClassDictMixin


@dataclass
class ClassA:
    name: str = "class_a"


@dataclass
class ClassB(DataClassDictMixin):
    class_a: Optional[ClassA] = field(
        default=None,
        metadata={
            "deserialize": lambda v: ClassA(name=v),
            "serialize": lambda v: v.name,
        },
    )
    phase: str = "first"


def test_optional_field():
    instance = ClassB.from_dict({"class_a": "testing"})
    assert instance
    assert instance.class_a.name == "testing"
    dct = instance.to_dict()
    assert dct["class_a"] == "testing"


def test_union_field():
    @dataclass
    class MyClass(DataClassDictMixin):
        status: Union[int, str, float] = field(
            metadata={
                "serialize": lambda v: str(v),
                "deserialize": lambda v: v,
            }
        )
        name: str = "testing"

    instance = MyClass(status=1)
    assert instance
    dct = instance.to_dict()
    assert isinstance(dct["status"], str)
