from dataclasses import dataclass
from datetime import date
from typing import Optional

import pytest
from typing_extensions import Literal

from mashumaro import DataClassDictMixin
from mashumaro.codecs.basic import decode
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
class _VariantBySubtypes:
    class Config(BaseConfig):
        discriminator = Discriminator(include_subtypes=True)


@dataclass
class VariantBySubtypesSub1(VariantBySubtypes):
    x: str
    type: Literal[1] = 1


@dataclass
class _VariantBySubtypesSub1(_VariantBySubtypes):
    x: str
    type: Literal[1] = 1


@dataclass
class VariantBySubtypesSub2(VariantBySubtypesSub1):
    x: date
    type: Literal[2] = 2


@dataclass
class _VariantBySubtypesSub2(_VariantBySubtypesSub1):
    x: date
    type: Literal[2] = 2


@dataclass
class VariantBySubtypesSub3(VariantBySubtypes):
    x: date
    type: Literal[3] = 3

    class Config(BaseConfig):
        discriminator = Discriminator(include_subtypes=True)


@dataclass
class _VariantBySubtypesSub3(_VariantBySubtypes):
    x: date
    type: Literal[3] = 3

    class Config(BaseConfig):
        discriminator = Discriminator(include_subtypes=True)


@dataclass
class VariantBySubtypesSub4(VariantBySubtypesSub3):
    pass


@dataclass
class _VariantBySubtypesSub4(_VariantBySubtypesSub3):
    pass


@dataclass
class VariantByFieldWithSubtypes(DataClassDictMixin):
    class Config(BaseConfig):
        discriminator = Discriminator(field="type", include_subtypes=True)


@dataclass
class _VariantByFieldWithSubtypes:
    class Config(BaseConfig):
        discriminator = Discriminator(field="type", include_subtypes=True)


@dataclass
class VariantByFieldWithSubtypesSub1(VariantByFieldWithSubtypes):
    x: Optional[str] = None
    type: Literal[1] = 1


@dataclass
class _VariantByFieldWithSubtypesSub1(_VariantByFieldWithSubtypes):
    x: Optional[str] = None
    type: Literal[1] = 1


@dataclass
class VariantByFieldWithSubtypesSub2(VariantByFieldWithSubtypesSub1):
    x: Optional[date] = None
    type: Literal[2] = 2


@dataclass
class _VariantByFieldWithSubtypesSub2(_VariantByFieldWithSubtypesSub1):
    x: Optional[date] = None
    type: Literal[2] = 2


@dataclass
class VariantByFieldWithSubtypesSub3(VariantByFieldWithSubtypes):
    x: Optional[date] = None
    type: Literal[3] = 3

    class Config(BaseConfig):
        discriminator = Discriminator(field="type", include_subtypes=True)


@dataclass
class _VariantByFieldWithSubtypesSub3(_VariantByFieldWithSubtypes):
    x: Optional[date] = None
    type: Literal[3] = 3

    class Config(BaseConfig):
        discriminator = Discriminator(field="type", include_subtypes=True)


@dataclass
class VariantByFieldWithSubtypesSub4(VariantByFieldWithSubtypesSub3):
    pass


@dataclass
class _VariantByFieldWithSubtypesSub4(_VariantByFieldWithSubtypesSub3):
    pass


@dataclass
class VariantByFieldWithSupertypesAndSubtypes(DataClassDictMixin):
    type: Literal["unknown"] = "unknown"

    class Config(BaseConfig):
        discriminator = Discriminator(
            field="type", include_supertypes=True, include_subtypes=True
        )


@dataclass
class _VariantByFieldWithSupertypesAndSubtypes:
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
class _VariantByFieldWithSupertypesAndSubtypesSub1(
    _VariantByFieldWithSupertypesAndSubtypes
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
class _VariantByFieldWithSupertypesAndSubtypesSub2(
    _VariantByFieldWithSupertypesAndSubtypesSub1
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
class _VariantByFieldWithSupertypesAndSubtypesSub3(
    _VariantByFieldWithSupertypesAndSubtypes
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
class _VariantByFieldWithSupertypesAndSubtypesSub4(
    _VariantByFieldWithSupertypesAndSubtypesSub3
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
class _VariantBySupertypesAndSubtypes:
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
class _VariantBySupertypesAndSubtypesSub1(_VariantBySupertypesAndSubtypes):
    x: Optional[str] = None
    type: Literal[1] = 1


@dataclass
class VariantBySupertypesAndSubtypesSub2(VariantBySupertypesAndSubtypesSub1):
    x: Optional[date] = None
    type: Literal[2] = 2


@dataclass
class _VariantBySupertypesAndSubtypesSub2(_VariantBySupertypesAndSubtypesSub1):
    x: Optional[date] = None
    type: Literal[2] = 2


@dataclass
class Foo1(DataClassDictMixin):
    x1: int

    class Config(BaseConfig):
        discriminator = Discriminator(field="type", include_subtypes=True)


@dataclass
class _Foo1:
    x1: int

    class Config(BaseConfig):
        discriminator = Discriminator(field="type", include_subtypes=True)


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
class Bar1(DataClassDictMixin):
    x1: int

    class Config(BaseConfig):
        discriminator = Discriminator(include_subtypes=True)


@dataclass
class _Bar1:
    x1: int

    class Config(BaseConfig):
        discriminator = Discriminator(include_subtypes=True)


@dataclass
class Bar2(Bar1):
    x2: int


@dataclass
class _Bar2(_Bar1):
    x2: int


@dataclass
class Bar3(Bar2):
    x: int
    type = 3


@dataclass
class _Bar3(_Bar2):
    x: int
    type = 3


@dataclass
class Bar4(Bar2):
    x: int
    type = 4


@dataclass
class _Bar4(_Bar2):
    x: int
    type = 4


@dataclass
class VariantWitCustomTagger(DataClassDictMixin):
    class Config(BaseConfig):
        discriminator = Discriminator(
            field="type",
            include_subtypes=True,
            variant_tagger_fn=lambda cls: cls.__name__.lower(),
        )


@dataclass
class _VariantWitCustomTagger:
    class Config(BaseConfig):
        discriminator = Discriminator(
            field="type",
            include_subtypes=True,
            variant_tagger_fn=lambda cls: cls.__name__.lower(),
        )


@dataclass
class VariantWitCustomTaggerSub1(VariantWitCustomTagger):
    pass


@dataclass
class _VariantWitCustomTaggerSub1(_VariantWitCustomTagger):
    pass


@dataclass
class VariantWitCustomTaggerSub2(VariantWitCustomTagger):
    pass


@dataclass
class _VariantWitCustomTaggerSub2(_VariantWitCustomTagger):
    pass


@dataclass
class VariantWithMultipleTags(DataClassDictMixin):
    class Config(BaseConfig):
        discriminator = Discriminator(
            field="type",
            include_subtypes=True,
            variant_tagger_fn=lambda cls: [
                cls.__name__.lower(),
                cls.__name__.upper(),
            ],
        )


@dataclass
class VariantWithMultipleTagsOne(VariantWithMultipleTags):
    pass


@dataclass
class VariantWithMultipleTagsTwo(VariantWithMultipleTags):
    pass


@dataclass
class _VariantWithMultipleTags:
    class Config(BaseConfig):
        discriminator = Discriminator(
            field="type",
            include_subtypes=True,
            variant_tagger_fn=lambda cls: [
                cls.__name__.lower(),
                cls.__name__.upper(),
            ],
        )


@dataclass
class _VariantWithMultipleTagsOne(_VariantWithMultipleTags):
    pass


@dataclass
class _VariantWithMultipleTagsTwo(_VariantWithMultipleTags):
    pass


def test_by_subtypes():
    assert VariantBySubtypes.from_dict(X_1) == VariantBySubtypesSub1(x=DT_STR)
    assert decode(X_1, _VariantBySubtypes) == _VariantBySubtypesSub1(x=DT_STR)

    assert VariantBySubtypes.from_dict(X_2) == VariantBySubtypesSub2(x=DT_DATE)
    assert decode(X_2, _VariantBySubtypes) == _VariantBySubtypesSub2(x=DT_DATE)

    assert VariantBySubtypes.from_dict(X_3) == VariantBySubtypesSub4(DT_DATE)
    assert decode(X_3, _VariantBySubtypes) == _VariantBySubtypesSub4(DT_DATE)

    assert VariantBySubtypesSub3.from_dict(X_3) == VariantBySubtypesSub4(
        DT_DATE
    )
    assert decode(X_3, _VariantBySubtypesSub3) == _VariantBySubtypesSub4(
        DT_DATE
    )

    with pytest.raises(SuitableVariantNotFoundError):
        VariantBySubtypesSub3.from_dict(X_1)
    with pytest.raises(SuitableVariantNotFoundError):
        decode(X_1, _VariantBySubtypesSub3)

    with pytest.raises(SuitableVariantNotFoundError):
        VariantBySubtypesSub3.from_dict(X_2)
    with pytest.raises(SuitableVariantNotFoundError):
        decode(X_2, _VariantBySubtypesSub3)

    @dataclass
    class MyClass(DataClassDictMixin):
        x: VariantBySubtypes

    @dataclass
    class _MyClass:
        x: _VariantBySubtypes

    assert MyClass.from_dict({"x": X_1}) == MyClass(
        VariantBySubtypesSub1(DT_STR)
    )
    assert decode({"x": X_1}, _MyClass) == _MyClass(
        _VariantBySubtypesSub1(DT_STR)
    )

    assert MyClass.from_dict({"x": X_2}) == MyClass(
        VariantBySubtypesSub2(DT_DATE)
    )
    assert decode({"x": X_2}, _MyClass) == _MyClass(
        _VariantBySubtypesSub2(DT_DATE)
    )

    assert MyClass.from_dict({"x": X_3}) == MyClass(
        VariantBySubtypesSub4(DT_DATE)
    )
    assert decode({"x": X_3}, _MyClass) == _MyClass(
        _VariantBySubtypesSub4(DT_DATE)
    )

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": {}})
    with pytest.raises(InvalidFieldValue):
        decode({"x": {}}, _MyClass)


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
    assert decode(
        X_1, _VariantByFieldWithSubtypes
    ) == _VariantByFieldWithSubtypesSub1(x=DT_STR)

    assert VariantByFieldWithSubtypes.from_dict(
        X_2
    ) == VariantByFieldWithSubtypesSub2(x=DT_DATE)
    assert decode(
        X_2, _VariantByFieldWithSubtypes
    ) == _VariantByFieldWithSubtypesSub2(x=DT_DATE)

    with pytest.raises(SuitableVariantNotFoundError):
        VariantByFieldWithSubtypes.from_dict(X_3)
    with pytest.raises(SuitableVariantNotFoundError):
        decode(X_3, _VariantByFieldWithSubtypes)

    with pytest.raises(SuitableVariantNotFoundError):
        VariantByFieldWithSubtypesSub3.from_dict(X_3)
    with pytest.raises(SuitableVariantNotFoundError):
        decode(X_3, _VariantByFieldWithSubtypesSub3)

    with pytest.raises(SuitableVariantNotFoundError):
        VariantByFieldWithSubtypesSub3.from_dict(X_1)
    with pytest.raises(SuitableVariantNotFoundError):
        decode(X_1, _VariantByFieldWithSubtypesSub3)

    @dataclass
    class MyClass(DataClassDictMixin):
        x: VariantByFieldWithSubtypes

    @dataclass
    class _MyClass:
        x: _VariantByFieldWithSubtypes

    assert MyClass.from_dict({"x": X_1}) == MyClass(
        VariantByFieldWithSubtypesSub1(DT_STR)
    )
    assert decode({"x": X_1}, _MyClass) == _MyClass(
        _VariantByFieldWithSubtypesSub1(DT_STR)
    )

    assert MyClass.from_dict({"x": X_2}) == MyClass(
        VariantByFieldWithSubtypesSub2(DT_DATE)
    )
    assert decode({"x": X_2}, _MyClass) == _MyClass(
        _VariantByFieldWithSubtypesSub2(DT_DATE)
    )

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": X_3})
    with pytest.raises(InvalidFieldValue):
        decode({"x": X_3}, _MyClass)

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": {}})
    with pytest.raises(InvalidFieldValue):
        decode({"x": {}}, _MyClass)


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
    assert decode(
        X_1, _VariantByFieldWithSupertypesAndSubtypes
    ) == _VariantByFieldWithSupertypesAndSubtypesSub1(x=DT_STR)

    assert VariantByFieldWithSupertypesAndSubtypes.from_dict(
        X_2
    ) == VariantByFieldWithSupertypesAndSubtypesSub2(x=DT_DATE)
    assert decode(
        X_2, _VariantByFieldWithSupertypesAndSubtypes
    ) == _VariantByFieldWithSupertypesAndSubtypesSub2(x=DT_DATE)

    with pytest.raises(SuitableVariantNotFoundError):
        VariantByFieldWithSupertypesAndSubtypes.from_dict(X_3)
    with pytest.raises(SuitableVariantNotFoundError):
        decode(X_3, _VariantByFieldWithSupertypesAndSubtypes)

    with pytest.raises(SuitableVariantNotFoundError):
        VariantByFieldWithSupertypesAndSubtypesSub3.from_dict(X_3)
    with pytest.raises(SuitableVariantNotFoundError):
        decode(X_3, _VariantByFieldWithSupertypesAndSubtypesSub3)

    with pytest.raises(SuitableVariantNotFoundError):
        VariantByFieldWithSupertypesAndSubtypesSub3.from_dict(X_1)
    with pytest.raises(SuitableVariantNotFoundError):
        decode(X_1, _VariantByFieldWithSupertypesAndSubtypesSub3)

    @dataclass
    class MyClass(DataClassDictMixin):
        x: VariantByFieldWithSupertypesAndSubtypes

    @dataclass
    class _MyClass:
        x: _VariantByFieldWithSupertypesAndSubtypes

    assert MyClass.from_dict({"x": X_1}) == MyClass(
        VariantByFieldWithSupertypesAndSubtypesSub1(x=DT_STR)
    )
    assert decode({"x": X_1}, _MyClass) == _MyClass(
        _VariantByFieldWithSupertypesAndSubtypesSub1(x=DT_STR)
    )

    assert MyClass.from_dict({"x": X_2}) == MyClass(
        VariantByFieldWithSupertypesAndSubtypesSub2(x=DT_DATE)
    )
    assert decode({"x": X_2}, _MyClass) == _MyClass(
        _VariantByFieldWithSupertypesAndSubtypesSub2(x=DT_DATE)
    )

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": X_3})
    with pytest.raises(InvalidFieldValue):
        decode({"x": X_3}, _MyClass)

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": {"type": "unknown"}})
    with pytest.raises(InvalidFieldValue):
        decode({"x": {"type": "unknown"}}, _MyClass)

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": {}})
    with pytest.raises(InvalidFieldValue):
        decode({"x": {}}, _MyClass)

    with pytest.raises(InvalidFieldValue):
        MyClass.from_dict({"x": {"type": "invalid"}})
    with pytest.raises(InvalidFieldValue):
        decode({"x": {"type": "invalid"}}, _MyClass)


def test_by_supertypes_and_subtypes():
    assert VariantBySupertypesAndSubtypes.from_dict(
        X_1
    ) == VariantBySupertypesAndSubtypesSub1(x=DT_STR)
    assert decode(
        X_1, _VariantBySupertypesAndSubtypes
    ) == _VariantBySupertypesAndSubtypesSub1(x=DT_STR)

    assert VariantBySupertypesAndSubtypes.from_dict(
        X_2
    ) == VariantBySupertypesAndSubtypesSub2(x=DT_DATE)
    assert decode(
        X_2, _VariantBySupertypesAndSubtypes
    ) == _VariantBySupertypesAndSubtypesSub2(x=DT_DATE)

    @dataclass
    class MyClass(DataClassDictMixin):
        x: VariantBySupertypesAndSubtypes

    @dataclass
    class _MyClass:
        x: _VariantBySupertypesAndSubtypes

    assert MyClass.from_dict({"x": X_1}) == MyClass(
        VariantBySupertypesAndSubtypesSub1(x=DT_STR)
    )
    assert decode({"x": X_1}, _MyClass) == _MyClass(
        _VariantBySupertypesAndSubtypesSub1(x=DT_STR)
    )

    assert MyClass.from_dict({"x": X_2}) == MyClass(
        VariantBySupertypesAndSubtypesSub2(x=DT_DATE)
    )
    assert decode({"x": X_2}, _MyClass) == _MyClass(
        _VariantBySupertypesAndSubtypesSub2(x=DT_DATE)
    )

    assert MyClass.from_dict({"x": {}}) == MyClass(
        VariantBySupertypesAndSubtypesSub1()
    )
    assert decode({"x": {}}, _MyClass) == _MyClass(
        _VariantBySupertypesAndSubtypesSub1()
    )


def test_subclass_tree_with_class_without_field():
    assert Foo1.from_dict({"type": 3, "x1": 1, "x2": 2, "x": 42}) == Foo3(
        1, 2, 42
    )
    assert decode({"type": 3, "x1": 1, "x2": 2, "x": 42}, _Foo1) == _Foo3(
        1, 2, 42
    )

    assert Foo1.from_dict({"type": 4, "x1": 1, "x2": 2, "x": 42}) == Foo4(
        1, 2, 42
    )
    assert decode({"type": 4, "x1": 1, "x2": 2, "x": 42}, _Foo1) == _Foo4(
        1, 2, 42
    )

    assert Bar1.from_dict({"type": 3, "x1": 1, "x2": 2, "x": 42}) == Bar2(1, 2)
    assert decode({"type": 3, "x1": 1, "x2": 2, "x": 42}, _Bar1) == _Bar2(1, 2)
    assert Bar1.from_dict({"type": 4, "x1": 1, "x2": 2, "x": 42}) == Bar2(1, 2)
    assert decode({"type": 4, "x1": 1, "x2": 2, "x": 42}, _Bar1) == _Bar2(1, 2)


def test_by_subtypes_with_custom_variant_tagger():
    assert (
        VariantWitCustomTagger.from_dict(
            {"type": "variantwitcustomtaggersub1"}
        )
        == VariantWitCustomTaggerSub1()
    )
    assert (
        decode(
            {"type": "_variantwitcustomtaggersub1"}, _VariantWitCustomTagger
        )
        == _VariantWitCustomTaggerSub1()
    )

    assert (
        VariantWitCustomTagger.from_dict(
            {"type": "variantwitcustomtaggersub2"}
        )
        == VariantWitCustomTaggerSub2()
    )
    assert (
        decode(
            {"type": "_variantwitcustomtaggersub2"}, _VariantWitCustomTagger
        )
        == _VariantWitCustomTaggerSub2()
    )

    with pytest.raises(SuitableVariantNotFoundError):
        VariantWitCustomTagger.from_dict({"type": "unknown"})
    with pytest.raises(SuitableVariantNotFoundError):
        decode({"type": "unknown"}, _VariantWitCustomTagger)


def test_by_subtypes_with_custom_variant_tagger_and_multiple_tags():
    for variant in (VariantWithMultipleTagsOne, VariantWithMultipleTagsTwo):
        for tag in (variant.__name__.lower(), variant.__name__.upper()):
            assert (
                VariantWithMultipleTags.from_dict({"type": tag}) == variant()
            )
    for variant in (_VariantWithMultipleTagsOne, _VariantWithMultipleTagsTwo):
        for tag in (variant.__name__.lower(), variant.__name__.upper()):
            assert decode({"type": tag}, _VariantWithMultipleTags) == variant()

    with pytest.raises(SuitableVariantNotFoundError):
        VariantWithMultipleTags.from_dict({"type": "unknown"})
    with pytest.raises(SuitableVariantNotFoundError):
        decode({"type": "unknown"}, _VariantWithMultipleTags)
