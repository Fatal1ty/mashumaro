from dataclasses import dataclass
from datetime import date

import pytest
from typing_extensions import Annotated, Literal

from mashumaro import DataClassDictMixin
from mashumaro.codecs.basic import decode
from mashumaro.exceptions import InvalidFieldValue
from mashumaro.types import Discriminator

DT_STR = "2023-05-30"
DT_DATE = date(2023, 5, 30)

X_STR_1 = {"x": DT_STR, "type": "str_1"}
X_STR_12 = {"x": DT_STR, "type": "str_12"}
X_DATE_12 = {"x": DT_STR, "type": "date_12"}
X_DATE_1 = {"x": DT_STR, "type": "date_1"}
X_STR_21 = {"x": DT_STR, "type": "str_21"}
X_DATE_22 = {"x": DT_STR, "type": "date_22"}


@dataclass
class BaseVariant(DataClassDictMixin):
    pass


@dataclass
class _BaseVariant:
    pass


@dataclass
class VariantStr1(BaseVariant):
    x: str
    type: Literal["str_1"] = "str_1"


@dataclass
class _VariantStr1(_BaseVariant):
    x: str
    type: Literal["str_1"] = "str_1"


@dataclass
class VariantDate1(BaseVariant):
    x: date
    type: Literal["date_1"] = "date_1"


@dataclass
class _VariantDate1(_BaseVariant):
    x: date
    type: Literal["date_1"] = "date_1"


@dataclass
class VariantStr12(VariantStr1):
    x: str
    type: Literal["str_12"] = "str_12"


@dataclass
class _VariantStr12(_VariantStr1):
    x: str
    type: Literal["str_12"] = "str_12"


@dataclass
class VariantDate12(VariantStr1):
    x: date
    type: Literal["date_12"] = "date_12"


@dataclass
class _VariantDate12(_VariantStr1):
    x: date
    type: Literal["date_12"] = "date_12"


@dataclass
class VariantStr21(VariantDate1):
    x: str
    type: Literal["str_21"] = "str_21"


@dataclass
class _VariantStr21(_VariantDate1):
    x: str
    type: Literal["str_21"] = "str_21"


@dataclass
class VariantDate22(VariantDate1):
    x: date
    type: Literal["date_22"] = "date_22"


@dataclass
class _VariantDate22(_VariantDate1):
    x: date
    type: Literal["date_22"] = "date_22"


@dataclass
class BySubtypes(DataClassDictMixin):
    x: Annotated[BaseVariant, Discriminator(include_subtypes=True)]


@dataclass
class _BySubtypes:
    x: Annotated[_BaseVariant, Discriminator(include_subtypes=True)]


@dataclass
class BySupertypes(DataClassDictMixin):
    x: Annotated[BaseVariant, Discriminator(include_supertypes=True)]
    x1: Annotated[VariantStr1, Discriminator(include_supertypes=True)]
    x2: Annotated[VariantDate1, Discriminator(include_supertypes=True)]


@dataclass
class _BySupertypes:
    x: Annotated[_BaseVariant, Discriminator(include_supertypes=True)]
    x1: Annotated[_VariantStr1, Discriminator(include_supertypes=True)]
    x2: Annotated[_VariantDate1, Discriminator(include_supertypes=True)]


@dataclass
class ByFieldWithSubtypes(DataClassDictMixin):
    x: Annotated[
        BaseVariant, Discriminator(field="type", include_subtypes=True)
    ]


@dataclass
class _ByFieldWithSubtypes:
    x: Annotated[
        _BaseVariant, Discriminator(field="type", include_subtypes=True)
    ]


@dataclass
class ByFieldWithSupertypes(DataClassDictMixin):
    x1: Annotated[
        VariantStr1, Discriminator(field="type", include_supertypes=True)
    ]
    x2: Annotated[
        VariantDate1, Discriminator(field="type", include_supertypes=True)
    ]


@dataclass
class _ByFieldWithSupertypes:
    x1: Annotated[
        _VariantStr1, Discriminator(field="type", include_supertypes=True)
    ]
    x2: Annotated[
        _VariantDate1, Discriminator(field="type", include_supertypes=True)
    ]


@dataclass
class ByFieldWithSupertypesAndSubtypes(DataClassDictMixin):
    x1: Annotated[
        VariantStr1,
        Discriminator(
            field="type", include_supertypes=True, include_subtypes=True
        ),
    ]
    x2: Annotated[
        VariantDate1,
        Discriminator(
            field="type", include_supertypes=True, include_subtypes=True
        ),
    ]


@dataclass
class _ByFieldWithSupertypesAndSubtypes:
    x1: Annotated[
        _VariantStr1,
        Discriminator(
            field="type", include_supertypes=True, include_subtypes=True
        ),
    ]
    x2: Annotated[
        _VariantDate1,
        Discriminator(
            field="type", include_supertypes=True, include_subtypes=True
        ),
    ]


@dataclass
class BySupertypesAndSubtypes(DataClassDictMixin):
    x1: Annotated[
        VariantStr1,
        Discriminator(include_supertypes=True, include_subtypes=True),
    ]
    x2: Annotated[
        VariantDate1,
        Discriminator(include_supertypes=True, include_subtypes=True),
    ]


@dataclass
class _BySupertypesAndSubtypes:
    x1: Annotated[
        _VariantStr1,
        Discriminator(include_supertypes=True, include_subtypes=True),
    ]
    x2: Annotated[
        _VariantDate1,
        Discriminator(include_supertypes=True, include_subtypes=True),
    ]


@dataclass
class Foo1(DataClassDictMixin):
    x1: int


@dataclass
class _Foo1:
    x1: int


@dataclass
class Foo2(Foo1):
    x2: int


@dataclass
class _Foo2(_Foo1):
    x2: int


@dataclass
class Foo3(Foo2):
    x: int
    type = 3


@dataclass
class _Foo3(_Foo2):
    x: int
    type = 3


@dataclass
class Foo4(Foo2):
    x: int
    type = 4


@dataclass
class _Foo4(_Foo2):
    x: int
    type = 4


@dataclass
class Bar(DataClassDictMixin):
    baz1: Annotated[Foo1, Discriminator(field="type", include_subtypes=True)]
    baz2: Annotated[Foo1, Discriminator(include_subtypes=True)]


@dataclass
class _Bar:
    baz1: Annotated[_Foo1, Discriminator(field="type", include_subtypes=True)]
    baz2: Annotated[_Foo1, Discriminator(include_subtypes=True)]


@dataclass
class BaseVariantWitCustomTagger(DataClassDictMixin):
    pass


@dataclass
class _BaseVariantWitCustomTagger:
    pass


@dataclass
class VariantWitCustomTaggerSub1(BaseVariantWitCustomTagger):
    pass


@dataclass
class _VariantWitCustomTaggerSub1(_BaseVariantWitCustomTagger):
    pass


@dataclass
class VariantWitCustomTaggerSub2(BaseVariantWitCustomTagger):
    pass


@dataclass
class _VariantWitCustomTaggerSub2(_BaseVariantWitCustomTagger):
    pass


@dataclass
class VariantWitCustomTaggerOwner(DataClassDictMixin):
    x: Annotated[
        BaseVariantWitCustomTagger,
        Discriminator(
            field="type",
            include_subtypes=True,
            variant_tagger_fn=lambda cls: cls.__name__.lower(),
        ),
    ]


@dataclass
class _VariantWitCustomTaggerOwner:
    x: Annotated[
        _BaseVariantWitCustomTagger,
        Discriminator(
            field="type",
            include_subtypes=True,
            variant_tagger_fn=lambda cls: cls.__name__.lower(),
        ),
    ]


@pytest.mark.parametrize(
    ["variant_data", "variant"],
    [
        (X_STR_1, VariantStr1(DT_STR)),
        (X_STR_12, VariantStr12(DT_STR)),
        (X_DATE_12, VariantDate12(DT_DATE)),
        (X_DATE_1, VariantDate1(DT_DATE)),
        (X_STR_21, VariantStr21(DT_STR)),
        (X_DATE_22, VariantDate22(DT_DATE)),
    ],
)
def test_by_subtypes(variant_data, variant):
    assert BySubtypes.from_dict({"x": variant_data}) == BySubtypes(variant)


@pytest.mark.parametrize(
    ["variant_data", "variant"],
    [
        (X_STR_1, _VariantStr1(DT_STR)),
        (X_STR_12, _VariantStr12(DT_STR)),
        (X_DATE_12, _VariantDate12(DT_DATE)),
        (X_DATE_1, _VariantDate1(DT_DATE)),
        (X_STR_21, _VariantStr21(DT_STR)),
        (X_DATE_22, _VariantDate22(DT_DATE)),
    ],
)
def test_by_subtypes_with_decoder(variant_data, variant):
    assert decode({"x": variant_data}, _BySubtypes) == _BySubtypes(variant)


def test_by_subtypes_exceptions():
    with pytest.raises(InvalidFieldValue):
        BySubtypes.from_dict({"x": {"type": "unknown"}})
    with pytest.raises(InvalidFieldValue):
        decode({"x": {"type": "unknown"}}, _BySubtypes)


def test_by_supertypes():
    assert BySupertypes.from_dict(
        {"x": {}, "x1": X_STR_1, "x2": X_DATE_1}
    ) == BySupertypes(
        BaseVariant(), VariantStr1(DT_STR), VariantDate1(DT_DATE)
    )
    assert decode(
        {"x": {}, "x1": X_STR_1, "x2": X_DATE_1}, _BySupertypes
    ) == _BySupertypes(
        _BaseVariant(), _VariantStr1(DT_STR), _VariantDate1(DT_DATE)
    )

    assert BySupertypes.from_dict(
        {"x": X_STR_1, "x1": X_STR_1, "x2": X_DATE_1}
    ) == BySupertypes(
        BaseVariant(), VariantStr1(DT_STR), VariantDate1(DT_DATE)
    )
    assert decode(
        {"x": X_STR_1, "x1": X_STR_1, "x2": X_DATE_1}, _BySupertypes
    ) == _BySupertypes(
        _BaseVariant(), _VariantStr1(DT_STR), _VariantDate1(DT_DATE)
    )

    with pytest.raises(InvalidFieldValue) as exc_info:
        BySupertypes.from_dict({"x": {}, "x1": X_STR_12, "x2": X_DATE_1})
    assert exc_info.value.field_name == "x1"

    with pytest.raises(InvalidFieldValue) as exc_info:
        decode({"x": {}, "x1": X_STR_12, "x2": X_DATE_1}, _BySupertypes)
    assert exc_info.value.field_name == "x1"

    with pytest.raises(InvalidFieldValue) as exc_info:
        BySupertypes.from_dict({"x": {}, "x1": X_STR_1, "x2": X_DATE_22})
    assert exc_info.value.field_name == "x2"

    with pytest.raises(InvalidFieldValue) as exc_info:
        decode({"x": {}, "x1": X_STR_1, "x2": X_DATE_22}, _BySupertypes)
    assert exc_info.value.field_name == "x2"


@pytest.mark.parametrize(
    ["variant_data", "variant"],
    [
        (X_STR_1, VariantStr1(DT_STR)),
        (X_STR_12, VariantStr12(DT_STR)),
        (X_DATE_12, VariantDate12(DT_DATE)),
        (X_DATE_1, VariantDate1(DT_DATE)),
        (X_STR_21, VariantStr21(DT_STR)),
        (X_DATE_22, VariantDate22(DT_DATE)),
    ],
)
def test_by_field_with_subtypes(variant_data, variant):
    assert ByFieldWithSubtypes.from_dict(
        {"x": variant_data}
    ) == ByFieldWithSubtypes(variant)


@pytest.mark.parametrize(
    ["variant_data", "variant"],
    [
        (X_STR_1, _VariantStr1(DT_STR)),
        (X_STR_12, _VariantStr12(DT_STR)),
        (X_DATE_12, _VariantDate12(DT_DATE)),
        (X_DATE_1, _VariantDate1(DT_DATE)),
        (X_STR_21, _VariantStr21(DT_STR)),
        (X_DATE_22, _VariantDate22(DT_DATE)),
    ],
)
def test_by_field_with_subtypes_with_decoder(variant_data, variant):
    assert decode(
        {"x": variant_data}, _ByFieldWithSubtypes
    ) == _ByFieldWithSubtypes(variant)


def test_by_field_with_subtypes_exceptions():
    with pytest.raises(InvalidFieldValue):
        ByFieldWithSubtypes.from_dict({"x": {"type": "unknown"}})
    with pytest.raises(InvalidFieldValue):
        decode({"x": {"type": "unknown"}}, _ByFieldWithSubtypes)


def test_by_field_with_supertypes():
    assert ByFieldWithSupertypes.from_dict(
        {"x1": X_STR_1, "x2": X_DATE_1}
    ) == ByFieldWithSupertypes(VariantStr1(DT_STR), VariantDate1(DT_DATE))
    assert decode(
        {"x1": X_STR_1, "x2": X_DATE_1}, _ByFieldWithSupertypes
    ) == _ByFieldWithSupertypes(_VariantStr1(DT_STR), _VariantDate1(DT_DATE))

    with pytest.raises(InvalidFieldValue) as exc_info:
        ByFieldWithSupertypes.from_dict({"x1": X_STR_12, "x2": X_DATE_1})
    assert exc_info.value.field_name == "x1"

    with pytest.raises(InvalidFieldValue) as exc_info:
        decode({"x1": X_STR_12, "x2": X_DATE_1}, _ByFieldWithSupertypes)
    assert exc_info.value.field_name == "x1"

    with pytest.raises(InvalidFieldValue) as exc_info:
        ByFieldWithSupertypes.from_dict({"x1": X_STR_1, "x2": X_DATE_22})
    assert exc_info.value.field_name == "x2"

    with pytest.raises(InvalidFieldValue) as exc_info:
        decode({"x1": X_STR_1, "x2": X_DATE_22}, _ByFieldWithSupertypes)
    assert exc_info.value.field_name == "x2"


@pytest.mark.parametrize(
    ["dataclass_cls"],
    [[ByFieldWithSupertypesAndSubtypes], [BySupertypesAndSubtypes]],
)
def test_by_field_with_supertypes_and_subtypes(dataclass_cls):
    assert dataclass_cls.from_dict(
        {"x1": X_STR_1, "x2": X_DATE_1}
    ) == dataclass_cls(VariantStr1(DT_STR), VariantDate1(DT_DATE))

    assert dataclass_cls.from_dict(
        {"x1": X_STR_12, "x2": X_STR_21}
    ) == dataclass_cls(VariantStr12(DT_STR), VariantStr21(DT_STR))

    assert dataclass_cls.from_dict(
        {"x1": X_DATE_12, "x2": X_DATE_22}
    ) == dataclass_cls(VariantDate12(DT_DATE), VariantDate22(DT_DATE))

    with pytest.raises(InvalidFieldValue):
        dataclass_cls.from_dict({"x1": X_DATE_1, "x2": X_STR_1})

    with pytest.raises(InvalidFieldValue):
        dataclass_cls.from_dict({"x1": X_STR_21, "x2": X_STR_12})

    with pytest.raises(InvalidFieldValue):
        dataclass_cls.from_dict({"x1": X_DATE_22, "x2": X_DATE_12})


@pytest.mark.parametrize(
    ["dataclass_cls"],
    [[_ByFieldWithSupertypesAndSubtypes], [_BySupertypesAndSubtypes]],
)
def test_by_field_with_supertypes_and_subtypes_with_decoder(dataclass_cls):
    assert decode(
        {"x1": X_STR_1, "x2": X_DATE_1}, dataclass_cls
    ) == dataclass_cls(_VariantStr1(DT_STR), _VariantDate1(DT_DATE))

    assert decode(
        {"x1": X_STR_12, "x2": X_STR_21}, dataclass_cls
    ) == dataclass_cls(_VariantStr12(DT_STR), _VariantStr21(DT_STR))

    assert decode(
        {"x1": X_DATE_12, "x2": X_DATE_22}, dataclass_cls
    ) == dataclass_cls(_VariantDate12(DT_DATE), _VariantDate22(DT_DATE))

    with pytest.raises(InvalidFieldValue):
        decode({"x1": X_DATE_1, "x2": X_STR_1}, dataclass_cls)

    with pytest.raises(InvalidFieldValue):
        decode({"x1": X_STR_21, "x2": X_STR_12}, dataclass_cls)

    with pytest.raises(InvalidFieldValue):
        decode({"x1": X_DATE_22, "x2": X_DATE_12}, dataclass_cls)


def test_subclass_tree_with_class_without_field():
    assert Bar.from_dict(
        {
            "baz1": {"type": 4, "x1": 1, "x2": 2, "x": 42},
            "baz2": {"type": 4, "x1": 1, "x2": 2, "x": 42},
        }
    ) == Bar(baz1=Foo4(1, 2, 42), baz2=Foo2(1, 2))
    assert decode(
        {
            "baz1": {"type": 4, "x1": 1, "x2": 2, "x": 42},
            "baz2": {"type": 4, "x1": 1, "x2": 2, "x": 42},
        },
        _Bar,
    ) == _Bar(baz1=_Foo4(1, 2, 42), baz2=_Foo2(1, 2))


def test_by_field_with_custom_variant_tagger():
    assert VariantWitCustomTaggerOwner.from_dict(
        {"x": {"type": "variantwitcustomtaggersub1"}}
    ) == VariantWitCustomTaggerOwner(VariantWitCustomTaggerSub1())
    assert decode(
        {"x": {"type": "_variantwitcustomtaggersub1"}},
        _VariantWitCustomTaggerOwner,
    ) == _VariantWitCustomTaggerOwner(_VariantWitCustomTaggerSub1())

    assert VariantWitCustomTaggerOwner.from_dict(
        {"x": {"type": "variantwitcustomtaggersub2"}}
    ) == VariantWitCustomTaggerOwner(VariantWitCustomTaggerSub2())
    assert decode(
        {"x": {"type": "_variantwitcustomtaggersub2"}},
        _VariantWitCustomTaggerOwner,
    ) == _VariantWitCustomTaggerOwner(_VariantWitCustomTaggerSub2())

    with pytest.raises(InvalidFieldValue):
        VariantWitCustomTaggerOwner.from_dict({"x": {"type": "unknown"}})
    with pytest.raises(InvalidFieldValue):
        decode({"x": {"type": "unknown"}}, _VariantWitCustomTaggerOwner)
