from dataclasses import dataclass
from datetime import date
from typing import Optional

import pytest
from typing_extensions import Literal

from mashumaro import DataClassDictMixin
from mashumaro.config import BaseConfig
from mashumaro.exceptions import (
    InvalidFieldValue,
    SuitableVariantNotFoundError,
)
from mashumaro.types import Discriminator

DT_STR = "2023-05-30"
DT_DATE = date(2023, 5, 30)

X_1 = {"x": DT_STR, "type": 1}
X_2 = {"x": DT_STR, "type": 2}
X_3 = {"x": DT_STR, "type": 3}


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
class VariantBySubtypesSub3(VariantBySubtypes):
    x: date
    type: Literal[3] = 3

    class Config(BaseConfig):
        discriminator = Discriminator(include_subtypes=True)


@dataclass
class VariantBySubtypesSub4(VariantBySubtypesSub3):
    pass


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
class VariantByFieldWithSubtypesSub3(VariantByFieldWithSubtypes):
    x: Optional[date] = None
    type: Literal[3] = 3

    class Config(BaseConfig):
        discriminator = Discriminator(field="type", include_subtypes=True)


@dataclass
class VariantByFieldWithSubtypesSub4(VariantByFieldWithSubtypesSub3):
    pass


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
class VariantByFieldWithSupertypesAndSubtypesSub3(
    VariantByFieldWithSupertypesAndSubtypes
):
    x: Optional[date] = None
    type: Literal[3] = 3

    class Config(BaseConfig):
        discriminator = Discriminator(
            field="type", include_supertypes=True, include_subtypes=True
        )


@dataclass
class VariantByFieldWithSupertypesAndSubtypesSub4(
    VariantByFieldWithSupertypesAndSubtypesSub3
):
    pass


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
    assert VariantBySubtypes.from_dict(X_1) == VariantBySubtypesSub1(x=DT_STR)

    assert VariantBySubtypes.from_dict(X_2) == VariantBySubtypesSub2(x=DT_DATE)

    assert VariantBySubtypes.from_dict(X_3) == VariantBySubtypesSub4(DT_DATE)

    assert VariantBySubtypesSub3.from_dict(X_3) == VariantBySubtypesSub4(
        DT_DATE
    )

    with pytest.raises(SuitableVariantNotFoundError):
        VariantBySubtypesSub3.from_dict(X_1)

    with pytest.raises(SuitableVariantNotFoundError):
        VariantBySubtypesSub3.from_dict(X_2)

    @dataclass
    class MyClass(DataClassDictMixin):
        x: VariantBySubtypes

    assert MyClass.from_dict({"x": X_1}) == MyClass(
        VariantBySubtypesSub1(DT_STR)
    )

    assert MyClass.from_dict({"x": X_2}) == MyClass(
        VariantBySubtypesSub2(DT_DATE)
    )

    assert MyClass.from_dict({"x": X_3}) == MyClass(
        VariantBySubtypesSub4(DT_DATE)
    )

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": {}})


def test_by_supertypes():
    with pytest.raises(ValueError) as exc_info:

        @dataclass
        class VariantBySupertypes(DataClassDictMixin):
            class Config(BaseConfig):
                discriminator = Discriminator(include_supertypes=True)

    assert str(exc_info.value) == (
        "Config based discriminator must have 'include_subtypes' enabled"
    )


def test_by_field_with_subtypes():
    assert VariantByFieldWithSubtypes.from_dict(
        X_1
    ) == VariantByFieldWithSubtypesSub1(x=DT_STR)

    assert VariantByFieldWithSubtypes.from_dict(
        X_2
    ) == VariantByFieldWithSubtypesSub2(x=DT_DATE)

    assert VariantByFieldWithSubtypes.from_dict(
        X_3
    ) == VariantByFieldWithSubtypesSub4(x=DT_DATE)

    assert VariantByFieldWithSubtypesSub3.from_dict(
        X_3
    ) == VariantByFieldWithSubtypesSub4(x=DT_DATE)

    with pytest.raises(SuitableVariantNotFoundError):
        VariantByFieldWithSubtypesSub3.from_dict(X_1)

    @dataclass
    class MyClass(DataClassDictMixin):
        x: VariantByFieldWithSubtypes

    assert MyClass.from_dict({"x": X_1}) == MyClass(
        VariantByFieldWithSubtypesSub1(DT_STR)
    )

    assert MyClass.from_dict({"x": X_2}) == MyClass(
        VariantByFieldWithSubtypesSub2(DT_DATE)
    )

    assert MyClass.from_dict({"x": X_3}) == MyClass(
        VariantByFieldWithSubtypesSub4(DT_DATE)
    )

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": {}})


def test_by_field_with_supertypes():
    with pytest.raises(ValueError) as exc_info:

        @dataclass
        class VariantByFieldWithSupertypes(DataClassDictMixin):
            class Config(BaseConfig):
                discriminator = Discriminator(
                    field="type", include_supertypes=True
                )

    assert str(exc_info.value) == (
        "Config based discriminator must have 'include_subtypes' enabled"
    )


def test_by_field_with_supertypes_and_subtypes():
    assert VariantByFieldWithSupertypesAndSubtypes.from_dict(
        X_1
    ) == VariantByFieldWithSupertypesAndSubtypesSub1(x=DT_STR)

    assert VariantByFieldWithSupertypesAndSubtypes.from_dict(
        X_2
    ) == VariantByFieldWithSupertypesAndSubtypesSub2(x=DT_DATE)

    assert VariantByFieldWithSupertypesAndSubtypes.from_dict(
        X_3
    ) == VariantByFieldWithSupertypesAndSubtypesSub4(x=DT_DATE)

    assert VariantByFieldWithSupertypesAndSubtypesSub3.from_dict(
        X_3
    ) == VariantByFieldWithSupertypesAndSubtypesSub4(x=DT_DATE)

    with pytest.raises(SuitableVariantNotFoundError):
        VariantByFieldWithSupertypesAndSubtypesSub3.from_dict(X_1)

    @dataclass
    class MyClass(DataClassDictMixin):
        x: VariantByFieldWithSupertypesAndSubtypes

    assert MyClass.from_dict({"x": X_1}) == MyClass(
        VariantByFieldWithSupertypesAndSubtypesSub1(x=DT_STR)
    )

    assert MyClass.from_dict({"x": X_2}) == MyClass(
        VariantByFieldWithSupertypesAndSubtypesSub2(x=DT_DATE)
    )

    assert MyClass.from_dict({"x": X_3}) == MyClass(
        VariantByFieldWithSupertypesAndSubtypesSub4(x=DT_DATE)
    )

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": {"type": "unknown"}})

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": {}})

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": {"type": "invalid"}})


def test_by_supertypes_and_subtypes():
    assert VariantBySupertypesAndSubtypes.from_dict(
        X_1
    ) == VariantBySupertypesAndSubtypesSub1(x=DT_STR)

    assert VariantBySupertypesAndSubtypes.from_dict(
        X_2
    ) == VariantBySupertypesAndSubtypesSub2(x=DT_DATE)

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
