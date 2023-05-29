from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import ClassVar, Union, Tuple

import pytest
from typing_extensions import Annotated, Final, Literal

from mashumaro import DataClassDictMixin, Discriminator
from mashumaro.exceptions import InvalidFieldValue


class VariantType(str, Enum):
    STR = "str"
    DATE = "date"
    DATE_SUBTYPE = "date_subtype"


DT_STR = "2022-05-30"
DT_DATE = date(2022, 5, 30)
X_STR = {"x": "2022-05-30", "type": "str"}
X_DATE = {"x": "2022-05-30", "type": "date"}
X_DATE_SUBTYPE = {"x": "2022-05-30", "type": "date_subtype"}


@dataclass
class UnannotatedVariantStr(DataClassDictMixin):
    x: str
    type = "str"


@dataclass
class ClassVarVariantStr(DataClassDictMixin):
    x: str
    type: ClassVar[str] = "str"


# @dataclass
# class FinalVariantStr(DataClassDictMixin):
#     x: str
#     type: Final[str] = "str"


@dataclass
class LiteralVariantStr(DataClassDictMixin):
    x: str
    type: Literal["str"] = "str"


@dataclass
class EnumVariantStr(DataClassDictMixin):
    x: str
    type: VariantType = VariantType.STR


@dataclass
class UnannotatedVariantDate(DataClassDictMixin):
    x: date
    type = "date"


@dataclass
class ClassVarVariantDate(DataClassDictMixin):
    x: date
    type: ClassVar[str] = "date"


# @dataclass
# class FinalVariantDate(DataClassDictMixin):
#     x: date
#     type: Final[str] = "date"


@dataclass
class LiteralVariantDate(DataClassDictMixin):
    x: date
    type: Literal["date"] = "date"


@dataclass
class EnumVariantDate(DataClassDictMixin):
    x: date
    type: VariantType = VariantType.DATE


@dataclass
class UnannotatedVariantDateSubtype(UnannotatedVariantDate):
    x: date
    type = "date_subtype"


@dataclass
class ClassVarVariantDateSubtype(ClassVarVariantDate):
    x: date
    type: ClassVar[str] = "date_subtype"


# @dataclass
# class FinalVariantDateSubtype(FinalVariantDate):
#     x: date
#     type: Final[str] = "date_subtype"


@dataclass
class LiteralVariantDateSubtype(LiteralVariantDate):
    x: date
    type: Literal["date_subtype"] = "date_subtype"


@dataclass
class EnumVariantDateSubtype(EnumVariantDate):
    x: date
    type: VariantType = VariantType.DATE_SUBTYPE


@dataclass
class ByField(DataClassDictMixin):
    unannotated: Annotated[
        Union[UnannotatedVariantStr, UnannotatedVariantDate],
        Discriminator("type"),
    ]
    class_var: Annotated[
        Union[ClassVarVariantStr, ClassVarVariantDate], Discriminator("type")
    ]
    # final: Annotated[
    #     Union[FinalVariantStr, FinalVariantDate], Discriminator("type")
    # ]
    literal: Annotated[
        Union[LiteralVariantStr, LiteralVariantDate],
        Discriminator("type"),
    ]
    enum: Annotated[
        Union[EnumVariantStr, EnumVariantDate], Discriminator("type")
    ]


@dataclass
class ByFieldWithSubtypes(DataClassDictMixin):
    unannotated: Annotated[
        Union[UnannotatedVariantStr, UnannotatedVariantDate],
        Discriminator("type", include_subtypes=True),
    ]
    class_var: Annotated[
        Union[ClassVarVariantStr, ClassVarVariantDate],
        Discriminator("type", include_subtypes=True),
    ]
    # final: Annotated[
    #     Union[FinalVariantStr, FinalVariantDate],
    #     Discriminator("type", include_subtypes=True),
    # ]
    literal: Annotated[
        Union[LiteralVariantStr, LiteralVariantDate],
        Discriminator("type", include_subtypes=True),
    ]
    enum: Annotated[
        Union[EnumVariantStr, EnumVariantDate],
        Discriminator("type", include_subtypes=True),
    ]


@dataclass
class ByFieldAndByFieldWithSubtypes(DataClassDictMixin):
    x: Tuple[
        Annotated[
            Union[UnannotatedVariantStr, UnannotatedVariantDate],
            Discriminator("type"),
        ],
        Annotated[
            Union[UnannotatedVariantDate, UnannotatedVariantDateSubtype],
            Discriminator("type", include_subtypes=True),
        ],
    ]


def test_by_field():
    assert ByField.from_dict(
        {
            "unannotated": X_STR,
            "class_var": X_STR,
            "literal": X_STR,
            "final": X_STR,
            "enum": X_STR,
        }
    ) == ByField(
        unannotated=UnannotatedVariantStr(DT_STR),
        class_var=ClassVarVariantStr(DT_STR),
        literal=LiteralVariantStr(DT_STR),
        # final=FinalVariantStr(dt_str),
        enum=EnumVariantStr(DT_STR),
    )
    assert ByField.from_dict(
        {
            "unannotated": X_DATE,
            "class_var": X_DATE,
            "literal": X_DATE,
            "final": X_DATE,
            "enum": X_DATE,
        }
    ) == ByField(
        unannotated=UnannotatedVariantDate(DT_DATE),
        class_var=ClassVarVariantDate(DT_DATE),
        literal=LiteralVariantDate(DT_DATE),
        # final=FinalVariantDate(dt_date),
        enum=EnumVariantDate(DT_DATE),
    )
    with pytest.raises(InvalidFieldValue) as exc_info:
        ByField.from_dict(
            {"unannotated": {"x": "2022-05-30", "type": "date_subtype"}}
        )
    assert exc_info.value.field_name == "unannotated"


def test_by_field_with_subtypes():
    assert ByFieldWithSubtypes.from_dict(
        {
            "unannotated": X_STR,
            "class_var": X_STR,
            "literal": X_STR,
            "final": X_STR,
            "enum": X_STR,
        }
    ) == ByFieldWithSubtypes(
        unannotated=UnannotatedVariantStr(DT_STR),
        class_var=ClassVarVariantStr(DT_STR),
        literal=LiteralVariantStr(DT_STR),
        # final=FinalVariantStr(dt_str),
        enum=EnumVariantStr(DT_STR),
    )
    assert ByFieldWithSubtypes.from_dict(
        {
            "unannotated": X_DATE,
            "class_var": X_DATE,
            "literal": X_DATE,
            "final": X_DATE,
            "enum": X_DATE,
        }
    ) == ByFieldWithSubtypes(
        unannotated=UnannotatedVariantDate(DT_DATE),
        class_var=ClassVarVariantDate(DT_DATE),
        literal=LiteralVariantDate(DT_DATE),
        # final=FinalVariantDate(dt_date),
        enum=EnumVariantDate(DT_DATE),
    )
    assert ByFieldWithSubtypes.from_dict(
        {
            "unannotated": X_DATE_SUBTYPE,
            "class_var": X_DATE_SUBTYPE,
            "literal": X_DATE_SUBTYPE,
            "final": X_DATE_SUBTYPE,
            "enum": X_DATE_SUBTYPE,
        }
    ) == ByFieldWithSubtypes(
        unannotated=UnannotatedVariantDateSubtype(DT_DATE),
        class_var=ClassVarVariantDateSubtype(DT_DATE),
        literal=LiteralVariantDateSubtype(DT_DATE),
        # final=FinalVariantDateSubtype(dt_date),
        enum=EnumVariantDateSubtype(DT_DATE),
    )


def test_tuple_with_discriminated_elements():
    assert ByFieldAndByFieldWithSubtypes.from_dict(
        {"x": [X_STR, X_DATE_SUBTYPE]}
    ) == ByFieldAndByFieldWithSubtypes(
        (
            UnannotatedVariantStr(DT_STR),
            UnannotatedVariantDateSubtype(DT_DATE),
        ),
    )
    with pytest.raises(InvalidFieldValue):
        ByFieldAndByFieldWithSubtypes.from_dict(
            {"x": [X_DATE_SUBTYPE, X_DATE_SUBTYPE]}
        )
    with pytest.raises(InvalidFieldValue):
        ByFieldAndByFieldWithSubtypes.from_dict({"x": [X_DATE_SUBTYPE, X_STR]})
