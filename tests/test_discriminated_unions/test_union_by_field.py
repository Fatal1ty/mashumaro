from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import ClassVar, Tuple, Union

import pytest
from typing_extensions import Annotated, Final, Literal

from mashumaro import DataClassDictMixin
from mashumaro.codecs import BasicDecoder
from mashumaro.exceptions import InvalidFieldValue
from mashumaro.types import Discriminator

DT_STR = "2023-05-30"
DT_DATE = date(2023, 5, 30)

X_STR = {"x": "2023-05-30", "type": "str"}
X_DATE = {"x": "2023-05-30", "type": "date"}
X_DATE_SUBTYPE = {"x": "2023-05-30", "type": "date_subtype"}


class VariantType(str, Enum):
    STR = "str"
    DATE = "date"
    DATE_SUBTYPE = "date_subtype"


@dataclass
class UnannotatedVariantStr:
    x: str
    type = "str"


@dataclass
class ClassVarVariantStr:
    x: str
    type: ClassVar[str] = "str"


@dataclass
class FinalVariantStr:
    x: str
    type: Final[str] = "str"


@dataclass
class LiteralVariantStr:
    x: str
    type: Literal["str"] = "str"


@dataclass
class EnumVariantStr:
    x: str
    type: VariantType = VariantType.STR


@dataclass
class UnannotatedVariantDate:
    x: date
    type = "date"


@dataclass
class ClassVarVariantDate:
    x: date
    type: ClassVar[str] = "date"


@dataclass
class FinalVariantDate:
    x: date
    type: Final[str] = "date"


@dataclass
class LiteralVariantDate:
    x: date
    type: Literal["date"] = "date"


@dataclass
class EnumVariantDate:
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


@dataclass
class FinalVariantDateSubtype(FinalVariantDate):
    x: date
    type: Final[str] = "date_subtype"


@dataclass
class LiteralVariantDateSubtype(LiteralVariantDate):
    x: date
    type: Literal["date_subtype"] = "date_subtype"


@dataclass
class EnumVariantDateSubtype(EnumVariantDate):
    x: date
    type: VariantType = VariantType.DATE_SUBTYPE


@dataclass
class _ByFieldWithSupertypes:
    unannotated: Annotated[
        Union[UnannotatedVariantStr, UnannotatedVariantDate],
        Discriminator("type", include_supertypes=True),
    ]
    class_var: Annotated[
        Union[ClassVarVariantStr, ClassVarVariantDate],
        Discriminator("type", include_supertypes=True),
    ]
    final: Annotated[
        Union[FinalVariantStr, FinalVariantDate],
        Discriminator("type", include_supertypes=True),
    ]
    literal: Annotated[
        Union[LiteralVariantStr, LiteralVariantDate],
        Discriminator("type", include_supertypes=True),
    ]
    enum: Annotated[
        Union[EnumVariantStr, EnumVariantDate],
        Discriminator("type", include_supertypes=True),
    ]


@dataclass
class ByFieldWithSupertypes(_ByFieldWithSupertypes, DataClassDictMixin):
    pass


@dataclass
class _ByFieldWithSubtypes:
    unannotated: Annotated[
        Union[UnannotatedVariantStr, UnannotatedVariantDate],
        Discriminator("type", include_subtypes=True),
    ]
    class_var: Annotated[
        Union[ClassVarVariantStr, ClassVarVariantDate],
        Discriminator("type", include_subtypes=True),
    ]
    final: Annotated[
        Union[FinalVariantStr, FinalVariantDate],
        Discriminator("type", include_subtypes=True),
    ]
    literal: Annotated[
        Union[LiteralVariantStr, LiteralVariantDate],
        Discriminator("type", include_subtypes=True),
    ]
    enum: Annotated[
        Union[EnumVariantStr, EnumVariantDate],
        Discriminator("type", include_subtypes=True),
    ]


@dataclass
class ByFieldWithSubtypes(_ByFieldWithSubtypes, DataClassDictMixin):
    pass


@dataclass
class _BySupertypes:
    unannotated: Annotated[
        Union[UnannotatedVariantStr, UnannotatedVariantDate],
        Discriminator(include_supertypes=True),
    ]
    class_var: Annotated[
        Union[ClassVarVariantStr, ClassVarVariantDate],
        Discriminator(include_supertypes=True),
    ]
    final: Annotated[
        Union[FinalVariantStr, FinalVariantDate],
        Discriminator(include_supertypes=True),
    ]
    literal: Annotated[
        Union[LiteralVariantStr, LiteralVariantDate],
        Discriminator(include_supertypes=True),
    ]
    enum: Annotated[
        Union[EnumVariantStr, EnumVariantDate],
        Discriminator(include_supertypes=True),
    ]


@dataclass
class BySupertypes(_BySupertypes, DataClassDictMixin):
    pass


@dataclass
class _BySubtypes:
    unannotated: Annotated[
        Union[UnannotatedVariantStr, UnannotatedVariantDate],
        Discriminator(include_subtypes=True),
    ]
    class_var: Annotated[
        Union[ClassVarVariantStr, ClassVarVariantDate],
        Discriminator(include_subtypes=True),
    ]
    final: Annotated[
        Union[FinalVariantStr, FinalVariantDate],
        Discriminator(include_subtypes=True),
    ]
    literal: Annotated[
        Union[LiteralVariantStr, LiteralVariantDate],
        Discriminator(include_subtypes=True),
    ]
    enum: Annotated[
        Union[EnumVariantStr, EnumVariantDate],
        Discriminator(include_subtypes=True),
    ]


@dataclass
class BySubtypes(_BySubtypes, DataClassDictMixin):
    pass


@dataclass
class _BySupertypesAndSubtypes:
    unannotated: Annotated[
        Union[UnannotatedVariantStr, UnannotatedVariantDate],
        Discriminator(include_supertypes=True, include_subtypes=True),
    ]
    class_var: Annotated[
        Union[ClassVarVariantStr, ClassVarVariantDate],
        Discriminator(include_supertypes=True, include_subtypes=True),
    ]
    final: Annotated[
        Union[FinalVariantStr, FinalVariantDate],
        Discriminator(include_supertypes=True, include_subtypes=True),
    ]
    literal: Annotated[
        Union[LiteralVariantStr, LiteralVariantDate],
        Discriminator(include_supertypes=True, include_subtypes=True),
    ]
    enum: Annotated[
        Union[EnumVariantStr, EnumVariantDate],
        Discriminator(include_supertypes=True, include_subtypes=True),
    ]


@dataclass
class BySupertypesAndSubtypes(_BySupertypesAndSubtypes, DataClassDictMixin):
    pass


@dataclass
class _ByFieldWithSupertypesAndSubtypes:
    unannotated: Annotated[
        Union[UnannotatedVariantStr, UnannotatedVariantDate],
        Discriminator("type", include_supertypes=True, include_subtypes=True),
    ]
    class_var: Annotated[
        Union[ClassVarVariantStr, ClassVarVariantDate],
        Discriminator("type", include_supertypes=True, include_subtypes=True),
    ]
    final: Annotated[
        Union[FinalVariantStr, FinalVariantDate],
        Discriminator("type", include_supertypes=True, include_subtypes=True),
    ]
    literal: Annotated[
        Union[LiteralVariantStr, LiteralVariantDate],
        Discriminator("type", include_supertypes=True, include_subtypes=True),
    ]
    enum: Annotated[
        Union[EnumVariantStr, EnumVariantDate],
        Discriminator("type", include_supertypes=True, include_subtypes=True),
    ]


@dataclass
class ByFieldWithSupertypesAndSubtypes(
    _ByFieldWithSupertypesAndSubtypes, DataClassDictMixin
):
    pass


@dataclass
class _ByFieldAndByFieldWithSubtypesInOneField:
    x: Tuple[
        Annotated[
            Union[UnannotatedVariantStr, UnannotatedVariantDate],
            Discriminator("type", include_supertypes=True),
        ],
        Annotated[
            Union[UnannotatedVariantStr, UnannotatedVariantDate],
            Discriminator("type", include_subtypes=True),
        ],
    ]


@dataclass
class ByFieldAndByFieldWithSubtypesInOneField(
    _ByFieldAndByFieldWithSubtypesInOneField, DataClassDictMixin
):
    pass


@dataclass
class VariantWitCustomTagger1:
    pass


@dataclass
class VariantWitCustomTagger2:
    pass


@dataclass
class _VariantWitCustomTaggerOwner:
    x: Annotated[
        Union[VariantWitCustomTagger1, VariantWitCustomTagger2],
        Discriminator(
            field="type",
            include_supertypes=True,
            variant_tagger_fn=lambda cls: cls.__name__.lower(),
        ),
    ]


@dataclass
class VariantWitCustomTaggerOwner(
    _VariantWitCustomTaggerOwner, DataClassDictMixin
):
    pass


@dataclass
class _VariantWitCustomTaggerWithMultipleTagsOwner:
    x: Annotated[
        Union[VariantWitCustomTagger1, VariantWitCustomTagger2],
        Discriminator(
            field="type",
            include_supertypes=True,
            variant_tagger_fn=lambda cls: [
                cls.__name__.lower(),
                cls.__name__.upper(),
            ],
        ),
    ]


@dataclass
class VariantWitCustomTaggerWithMultipleTagsOwner(
    _VariantWitCustomTaggerWithMultipleTagsOwner, DataClassDictMixin
):
    pass


def test_by_field_with_supertypes():
    decoder = BasicDecoder(_ByFieldWithSupertypes)

    for func, cls in (
        (ByFieldWithSupertypes.from_dict, ByFieldWithSupertypes),
        (decoder.decode, _ByFieldWithSupertypes),
    ):
        assert func(
            {
                "unannotated": X_STR,
                "class_var": X_STR,
                "literal": X_STR,
                "final": X_STR,
                "enum": X_STR,
            }
        ) == cls(
            unannotated=UnannotatedVariantStr(DT_STR),
            class_var=ClassVarVariantStr(DT_STR),
            literal=LiteralVariantStr(DT_STR),
            final=FinalVariantStr(DT_STR),
            enum=EnumVariantStr(DT_STR),
        )

    for func, cls in (
        (ByFieldWithSupertypes.from_dict, ByFieldWithSupertypes),
        (decoder.decode, _ByFieldWithSupertypes),
    ):
        assert func(
            {
                "unannotated": X_DATE,
                "class_var": X_DATE,
                "literal": X_DATE,
                "final": X_DATE,
                "enum": X_DATE,
            }
        ) == cls(
            unannotated=UnannotatedVariantDate(DT_DATE),
            class_var=ClassVarVariantDate(DT_DATE),
            literal=LiteralVariantDate(DT_DATE),
            final=FinalVariantDate(DT_DATE),
            enum=EnumVariantDate(DT_DATE),
        )

    for func in (ByFieldWithSupertypes.from_dict, decoder.decode):
        with pytest.raises(InvalidFieldValue) as exc_info:
            func({"unannotated": {"x": "2023-05-30", "type": "date_subtype"}})
        assert exc_info.value.field_name == "unannotated"


def test_by_field_with_subtypes():
    decoder = BasicDecoder(_ByFieldWithSubtypes)

    for func, cls in (
        (ByFieldWithSubtypes.from_dict, ByFieldWithSubtypes),
        (decoder.decode, _ByFieldWithSubtypes),
    ):
        assert func(
            {
                "unannotated": X_DATE_SUBTYPE,
                "class_var": X_DATE_SUBTYPE,
                "literal": X_DATE_SUBTYPE,
                "final": X_DATE_SUBTYPE,
                "enum": X_DATE_SUBTYPE,
            }
        ) == cls(
            unannotated=UnannotatedVariantDateSubtype(DT_DATE),
            class_var=ClassVarVariantDateSubtype(DT_DATE),
            literal=LiteralVariantDateSubtype(DT_DATE),
            final=FinalVariantDateSubtype(DT_DATE),
            enum=EnumVariantDateSubtype(DT_DATE),
        )

    for func in (ByFieldWithSubtypes.from_dict, decoder.decode):
        with pytest.raises(InvalidFieldValue) as exc_info:
            func(
                {
                    "unannotated": X_STR,
                    "class_var": X_STR,
                    "literal": X_STR,
                    "final": X_STR,
                    "enum": X_STR,
                }
            )
        assert exc_info.value.field_name == "unannotated"

    for func in (ByFieldWithSubtypes.from_dict, decoder.decode):
        with pytest.raises(InvalidFieldValue) as exc_info:
            func(
                {
                    "unannotated": X_DATE,
                    "class_var": X_DATE,
                    "literal": X_DATE,
                    "final": X_DATE,
                    "enum": X_DATE,
                }
            )
        assert exc_info.value.field_name == "unannotated"


def test_by_field_with_supertypes_and_subtypes():
    decoder = BasicDecoder(_ByFieldWithSupertypesAndSubtypes)

    for func, cls in (
        (
            ByFieldWithSupertypesAndSubtypes.from_dict,
            ByFieldWithSupertypesAndSubtypes,
        ),
        (decoder.decode, _ByFieldWithSupertypesAndSubtypes),
    ):
        assert func(
            {
                "unannotated": X_STR,
                "class_var": X_STR,
                "literal": X_STR,
                "final": X_STR,
                "enum": X_STR,
            }
        ) == cls(
            unannotated=UnannotatedVariantStr(DT_STR),
            class_var=ClassVarVariantStr(DT_STR),
            literal=LiteralVariantStr(DT_STR),
            final=FinalVariantStr(DT_STR),
            enum=EnumVariantStr(DT_STR),
        )

    for func, cls in (
        (
            ByFieldWithSupertypesAndSubtypes.from_dict,
            ByFieldWithSupertypesAndSubtypes,
        ),
        (decoder.decode, _ByFieldWithSupertypesAndSubtypes),
    ):
        assert func(
            {
                "unannotated": X_DATE,
                "class_var": X_DATE,
                "literal": X_DATE,
                "final": X_DATE,
                "enum": X_DATE,
            }
        ) == cls(
            unannotated=UnannotatedVariantDate(DT_DATE),
            class_var=ClassVarVariantDate(DT_DATE),
            literal=LiteralVariantDate(DT_DATE),
            final=FinalVariantDate(DT_DATE),
            enum=EnumVariantDate(DT_DATE),
        )

    for func, cls in (
        (
            ByFieldWithSupertypesAndSubtypes.from_dict,
            ByFieldWithSupertypesAndSubtypes,
        ),
        (decoder.decode, _ByFieldWithSupertypesAndSubtypes),
    ):
        assert func(
            {
                "unannotated": X_DATE_SUBTYPE,
                "class_var": X_DATE_SUBTYPE,
                "literal": X_DATE_SUBTYPE,
                "final": X_DATE_SUBTYPE,
                "enum": X_DATE_SUBTYPE,
            }
        ) == cls(
            unannotated=UnannotatedVariantDateSubtype(DT_DATE),
            class_var=ClassVarVariantDateSubtype(DT_DATE),
            literal=LiteralVariantDateSubtype(DT_DATE),
            final=FinalVariantDateSubtype(DT_DATE),
            enum=EnumVariantDateSubtype(DT_DATE),
        )


def test_by_supertypes():
    decoder = BasicDecoder(_BySupertypes)

    for func, cls in (
        (BySupertypes.from_dict, BySupertypes),
        (decoder.decode, _BySupertypes),
    ):
        assert func(
            {
                "unannotated": X_STR,
                "class_var": X_STR,
                "literal": X_STR,
                "final": X_STR,
                "enum": X_STR,
            }
        ) == cls(
            unannotated=UnannotatedVariantStr(DT_STR),
            class_var=ClassVarVariantStr(DT_STR),
            literal=LiteralVariantStr(DT_STR),
            final=FinalVariantStr(DT_STR),
            enum=EnumVariantStr(DT_STR),
        )

    for func, cls in (
        (BySupertypes.from_dict, BySupertypes),
        (decoder.decode, _BySupertypes),
    ):
        assert func(
            {
                "unannotated": X_DATE,
                "class_var": X_DATE,
                "literal": X_DATE,
                "final": X_DATE,
                "enum": X_DATE,
            }
        ) == cls(
            unannotated=UnannotatedVariantStr(DT_STR),
            class_var=ClassVarVariantStr(DT_STR),
            literal=LiteralVariantDate(DT_DATE),
            # final without field discriminator can lead to unexpected result
            final=FinalVariantStr(DT_STR, type=VariantType.DATE),
            # enum without field discriminator can lead to unexpected result
            enum=EnumVariantStr(DT_STR, type=VariantType.DATE),
        )

    for func in (BySupertypes.from_dict, decoder.decode):
        with pytest.raises(InvalidFieldValue) as exc_info:
            func(
                {
                    "unannotated": X_DATE_SUBTYPE,
                    "class_var": X_DATE_SUBTYPE,
                    "literal": X_DATE_SUBTYPE,
                    "final": X_DATE_SUBTYPE,
                    "enum": X_DATE_SUBTYPE,
                }
            )
        assert exc_info.value.field_name == "literal"


def test_by_subtypes():
    decoder = BasicDecoder(_BySubtypes)

    for func, cls in (
        (BySubtypes.from_dict, BySubtypes),
        (decoder.decode, _BySubtypes),
    ):
        assert func(
            {
                "unannotated": X_DATE_SUBTYPE,
                "class_var": X_DATE_SUBTYPE,
                "literal": X_DATE_SUBTYPE,
                "final": X_DATE_SUBTYPE,
                "enum": X_DATE_SUBTYPE,
            }
        ) == cls(
            unannotated=UnannotatedVariantDateSubtype(DT_DATE),
            class_var=ClassVarVariantDateSubtype(DT_DATE),
            literal=LiteralVariantDateSubtype(DT_DATE),
            final=FinalVariantDateSubtype(DT_DATE),
            enum=EnumVariantDateSubtype(DT_DATE),
        )

    for func, cls in (
        (BySubtypes.from_dict, BySubtypes),
        (decoder.decode, _BySubtypes),
    ):
        assert func(
            {
                "unannotated": X_DATE,
                "class_var": X_DATE,
                "literal": X_DATE_SUBTYPE,
                "final": X_DATE,
                "enum": X_DATE,
            }
        ) == cls(
            unannotated=UnannotatedVariantDateSubtype(DT_DATE),
            class_var=ClassVarVariantDateSubtype(DT_DATE),
            literal=LiteralVariantDateSubtype(DT_DATE),
            # final without field discriminator can lead to unexpected result
            final=FinalVariantDateSubtype(DT_DATE, type=VariantType.DATE),
            # enum without field discriminator can lead to unexpected result
            enum=EnumVariantDateSubtype(DT_DATE, type=VariantType.DATE),
        )

    for func in (BySubtypes.from_dict, decoder.decode):
        with pytest.raises(InvalidFieldValue) as exc_info:
            func(
                {
                    "unannotated": X_STR,
                    "class_var": X_STR,
                    "literal": X_STR,
                    "final": X_STR,
                    "enum": X_STR,
                }
            )
        assert exc_info.value.field_name == "literal"


def test_by_supertypes_and_subtypes():
    decoder = BasicDecoder(_BySupertypesAndSubtypes)

    for func, cls in (
        (BySupertypesAndSubtypes.from_dict, BySupertypesAndSubtypes),
        (decoder.decode, _BySupertypesAndSubtypes),
    ):
        assert func(
            {
                "unannotated": X_DATE_SUBTYPE,
                "class_var": X_DATE_SUBTYPE,
                "literal": X_DATE_SUBTYPE,
                "final": X_DATE_SUBTYPE,
                "enum": X_DATE_SUBTYPE,
            }
        ) == cls(
            unannotated=UnannotatedVariantDateSubtype(DT_DATE),
            class_var=ClassVarVariantDateSubtype(DT_DATE),
            literal=LiteralVariantDateSubtype(DT_DATE),
            final=FinalVariantDateSubtype(DT_DATE),
            enum=EnumVariantDateSubtype(DT_DATE),
        )

    for func, cls in (
        (BySupertypesAndSubtypes.from_dict, BySupertypesAndSubtypes),
        (decoder.decode, _BySupertypesAndSubtypes),
    ):
        assert func(
            {
                "unannotated": X_STR,
                "class_var": X_STR,
                "literal": X_STR,
                "final": X_STR,
                "enum": X_STR,
            }
        ) == cls(
            unannotated=UnannotatedVariantDateSubtype(DT_DATE),
            class_var=ClassVarVariantDateSubtype(DT_DATE),
            literal=LiteralVariantStr(DT_STR),
            # using final without field discriminator
            # can lead to unexpected result
            final=FinalVariantDateSubtype(DT_DATE, type=VariantType.STR),
            # using enum without field discriminator
            # can lead to unexpected result
            enum=EnumVariantDateSubtype(DT_DATE, type=VariantType.STR),
        )

    for func, cls in (
        (BySupertypesAndSubtypes.from_dict, BySupertypesAndSubtypes),
        (decoder.decode, _BySupertypesAndSubtypes),
    ):
        assert func(
            {
                "unannotated": X_DATE,
                "class_var": X_DATE,
                "literal": X_DATE,
                "final": X_DATE,
                "enum": X_DATE,
            }
        ) == cls(
            unannotated=UnannotatedVariantDateSubtype(DT_DATE),
            class_var=ClassVarVariantDateSubtype(DT_DATE),
            literal=LiteralVariantDate(DT_DATE),
            # final without field discriminator can lead to unexpected result
            final=FinalVariantDateSubtype(DT_DATE, type=VariantType.DATE),
            # enum without field discriminator can lead to unexpected result
            enum=EnumVariantDateSubtype(DT_DATE, type=VariantType.DATE),
        )


def test_tuple_with_discriminated_elements():
    decoder = BasicDecoder(_ByFieldAndByFieldWithSubtypesInOneField)

    for func, cls in (
        (
            ByFieldAndByFieldWithSubtypesInOneField.from_dict,
            ByFieldAndByFieldWithSubtypesInOneField,
        ),
        (decoder.decode, _ByFieldAndByFieldWithSubtypesInOneField),
    ):
        assert func({"x": [X_STR, X_DATE_SUBTYPE]}) == cls(
            (
                UnannotatedVariantStr(DT_STR),
                UnannotatedVariantDateSubtype(DT_DATE),
            ),
        )

    for func in (
        ByFieldAndByFieldWithSubtypesInOneField.from_dict,
        decoder.decode,
    ):
        with pytest.raises(InvalidFieldValue):
            func({"x": [X_DATE_SUBTYPE, X_DATE_SUBTYPE]})

    for func in (
        ByFieldAndByFieldWithSubtypesInOneField.from_dict,
        decoder.decode,
    ):
        with pytest.raises(InvalidFieldValue):
            func({"x": [X_STR, X_STR]})


def test_by_field_with_subtypes_with_custom_variant_tagger():
    decoder = BasicDecoder(_VariantWitCustomTaggerOwner)

    for func, cls in (
        (VariantWitCustomTaggerOwner.from_dict, VariantWitCustomTaggerOwner),
        (decoder.decode, _VariantWitCustomTaggerOwner),
    ):
        assert func({"x": {"type": "variantwitcustomtagger1"}}) == cls(
            VariantWitCustomTagger1()
        )
        assert func({"x": {"type": "variantwitcustomtagger2"}}) == cls(
            VariantWitCustomTagger2()
        )
        with pytest.raises(InvalidFieldValue):
            func({"x": {"type": "unknown"}})


def test_by_field_with_subtypes_with_custom_variant_tagger_and_multiple_tags():
    decoder = BasicDecoder(_VariantWitCustomTaggerWithMultipleTagsOwner)

    for func, cls in (
        (
            VariantWitCustomTaggerWithMultipleTagsOwner.from_dict,
            VariantWitCustomTaggerWithMultipleTagsOwner,
        ),
        (decoder.decode, _VariantWitCustomTaggerWithMultipleTagsOwner),
    ):
        assert func({"x": {"type": "variantwitcustomtagger1"}}) == cls(
            VariantWitCustomTagger1()
        )
        assert func({"x": {"type": "variantwitcustomtagger2"}}) == cls(
            VariantWitCustomTagger2()
        )
        assert func({"x": {"type": "VARIANTWITCUSTOMTAGGER1"}}) == cls(
            VariantWitCustomTagger1()
        )
        assert func({"x": {"type": "VARIANTWITCUSTOMTAGGER2"}}) == cls(
            VariantWitCustomTagger2()
        )
        with pytest.raises(InvalidFieldValue):
            func({"x": {"type": "unknown"}})
