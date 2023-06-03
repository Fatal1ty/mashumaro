from dataclasses import dataclass
from datetime import date
from typing import Optional

import pytest
from typing_extensions import Literal

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig
from mashumaro.exceptions import InvalidFieldValue
from mashumaro.types import Discriminator

DT_STR = "2022-05-30"
DT_DATE = date(2022, 5, 30)

X_1 = {"x": DT_STR, "type": 1}
X_2 = {"x": DT_STR, "type": 2}


@dataclass
class VariantBySubtypes(DataClassDictMixin):
    class Config(BaseConfig):
        discriminator = Discriminator(include_subtypes=True)


@dataclass
class VariantBySubtypesSub1(VariantBySubtypes):
    x: str
    type: Literal[1] = 1


@dataclass
class VariantBySubtypesSub2(VariantBySubtypesSub1):
    x: date
    type: Literal[2] = 2


@dataclass
class VariantBySupertypes(DataClassDictMixin):
    type: Literal["unknown"] = "unknown"

    class Config(BaseConfig):
        discriminator = Discriminator(include_supertypes=True)


@dataclass
class VariantBySupertypesSub1(VariantBySupertypes):
    x: Optional[str] = None
    type: Literal[1] = 1


@dataclass
class VariantBySupertypesSub2(VariantBySupertypesSub1):
    x: Optional[date] = None
    type: Literal[2] = 2


@dataclass
class VariantByFieldWithSubtypes(DataClassDictMixin):
    class Config(BaseConfig):
        discriminator = Discriminator(field="type", include_subtypes=True)


@dataclass
class VariantByFieldWithSubtypesSub1(VariantByFieldWithSubtypes):
    x: Optional[str] = None
    type: Literal[1] = 1


@dataclass
class VariantByFieldWithSubtypesSub2(VariantByFieldWithSubtypesSub1):
    x: Optional[date] = None
    type: Literal[2] = 2


@dataclass
class VariantByFieldWithSupertypes(DataClassDictMixin):
    type: Literal["unknown"] = "unknown"

    class Config(BaseConfig):
        discriminator = Discriminator(field="type", include_supertypes=True)


@dataclass
class VariantByFieldWithSupertypesSub1(VariantByFieldWithSupertypes):
    x: Optional[str] = None
    type: Literal[1] = 1


@dataclass
class VariantByFieldWithSupertypesSub2(VariantByFieldWithSupertypesSub1):
    x: Optional[date] = None
    type: Literal[2] = 2


@dataclass
class VariantByFieldWithSupertypesAndSubtypes(DataClassDictMixin):
    type: Literal["unknown"] = "unknown"

    class Config(BaseConfig):
        discriminator = Discriminator(
            field="type", include_supertypes=True, include_subtypes=True
        )


@dataclass
class VariantByFieldWithSupertypesAndSubtypesSub1(
    VariantByFieldWithSupertypesAndSubtypes
):
    x: Optional[str] = None
    type: Literal[1] = 1


@dataclass
class VariantByFieldWithSupertypesAndSubtypesSub2(
    VariantByFieldWithSupertypesAndSubtypesSub1
):
    x: Optional[date] = None
    type: Literal[2] = 2


@dataclass
class VariantBySupertypesAndSubtypes(DataClassDictMixin):
    type: Literal["unknown"] = "unknown"

    class Config(BaseConfig):
        discriminator = Discriminator(
            include_supertypes=True, include_subtypes=True
        )


@dataclass
class VariantBySupertypesAndSubtypesSub1(VariantBySupertypesAndSubtypes):
    x: Optional[str] = None
    type: Literal[1] = 1


@dataclass
class VariantBySupertypesAndSubtypesSub2(VariantBySupertypesAndSubtypesSub1):
    x: Optional[date] = None
    type: Literal[2] = 2


def test_by_subtypes():
    @dataclass
    class MyClass(DataClassDictMixin):
        x: VariantBySubtypes

    assert MyClass.from_dict({"x": X_1}) == MyClass(
        VariantBySubtypesSub1(DT_STR)
    )

    assert MyClass.from_dict({"x": X_2}) == MyClass(
        VariantBySubtypesSub2(DT_DATE)
    )

    with pytest.raises(InvalidFieldValue):
        assert MyClass.from_dict({"x": {}})


def test_by_supertypes():
    @dataclass
    class MyClass(DataClassDictMixin):
        x: VariantBySupertypes

    assert MyClass.from_dict({"x": {}}) == MyClass(VariantBySupertypes())

    assert MyClass.from_dict({"x": {"type": "unknown"}}) == MyClass(
        VariantBySupertypes()
    )

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": X_1})

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": X_2})

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": {"type": "invalid"}})


def test_by_field_with_subtypes():
    @dataclass
    class MyClass(DataClassDictMixin):
        x: VariantByFieldWithSubtypes

    assert MyClass.from_dict({"x": X_1}) == MyClass(
        VariantByFieldWithSubtypesSub1(DT_STR)
    )

    assert MyClass.from_dict({"x": X_2}) == MyClass(
        VariantByFieldWithSubtypesSub2(DT_DATE)
    )

    with pytest.raises(InvalidFieldValue):
        assert MyClass.from_dict({"x": {}})


def test_by_field_with_supertypes():
    @dataclass
    class MyClass(DataClassDictMixin):
        x: VariantByFieldWithSupertypes

    assert MyClass.from_dict({"x": {}}) == MyClass(
        VariantByFieldWithSupertypes()
    )

    assert MyClass.from_dict({"x": {"type": "unknown"}}) == MyClass(
        VariantByFieldWithSupertypes()
    )

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": X_1})

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": X_2})

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": {"type": "invalid"}})


def test_by_field_with_supertypes_and_subtypes():
    @dataclass
    class MyClass(DataClassDictMixin):
        x: VariantByFieldWithSupertypesAndSubtypes

    assert MyClass.from_dict({"x": X_1}) == MyClass(
        VariantByFieldWithSupertypesAndSubtypesSub1(x=DT_STR)
    )

    assert MyClass.from_dict({"x": X_2}) == MyClass(
        VariantByFieldWithSupertypesAndSubtypesSub2(x=DT_DATE)
    )

    with pytest.raises(InvalidFieldValue):
        # RecursionError
        MyClass.from_dict({"x": {"type": "unknown"}})

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": {}})

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": {"type": "invalid"}})


def test_by_supertypes_and_subtypes():
    @dataclass
    class MyClass(DataClassDictMixin):
        x: VariantBySupertypesAndSubtypes

    assert MyClass.from_dict({"x": X_1}) == MyClass(
        VariantBySupertypesAndSubtypesSub1(x=DT_STR)
    )

    assert MyClass.from_dict({"x": X_2}) == MyClass(
        VariantBySupertypesAndSubtypesSub2(x=DT_DATE)
    )

    assert MyClass.from_dict({"x": {}}) == MyClass(
        VariantBySupertypesAndSubtypesSub1()
    )
