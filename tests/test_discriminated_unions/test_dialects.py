from dataclasses import dataclass
from datetime import date
from typing import Dict, Union

from typing_extensions import Annotated, Literal

from mashumaro.codecs import BasicDecoder
from mashumaro.codecs.orjson import ORJSONDecoder
from mashumaro.config import ADD_DIALECT_SUPPORT, BaseConfig
from mashumaro.dialect import Dialect
from mashumaro.mixins.orjson import DataClassORJSONMixin
from mashumaro.types import Discriminator


class DefaultDialect(Dialect):
    serialization_strategy = {
        date: {
            "deserialize": date.fromisoformat,
            "serialize": date.isoformat,
        },
        dict: {
            "deserialize": lambda x: {k: v for k, v in x},
            "serialize": lambda x: [(k, v) for k, v in x.items()],
        },
    }


class MyDialect(Dialect):
    serialization_strategy = {
        date: {
            "deserialize": date.fromordinal,
            "serialize": date.toordinal,
        },
        dict: {
            "deserialize": dict,
            "serialize": dict,
        },
    }


@dataclass
class Variant1(DataClassORJSONMixin):
    x: date
    y: Dict[str, int]

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]
        dialect = DefaultDialect
        discriminator = Discriminator(field="type", include_subtypes=True)


@dataclass
class _Variant1:
    x: date
    y: Dict[str, int]

    class Config(BaseConfig):
        discriminator = Discriminator(field="type", include_subtypes=True)


@dataclass
class Variant1Subtype1(Variant1):
    type: Literal[1] = 1


@dataclass
class _Variant1Subtype1(_Variant1):
    type: Literal[1] = 1


@dataclass
class Variant2(DataClassORJSONMixin):
    x: date
    y: Dict[str, int]

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]
        dialect = DefaultDialect


@dataclass
class _Variant2:
    x: date
    y: Dict[str, int]

    class Config(BaseConfig):
        dialect = DefaultDialect


@dataclass
class Variant2Subtype1(Variant2):
    type: Literal[1] = 1


@dataclass
class _Variant2Subtype1(_Variant2):
    type: Literal[1] = 1


@dataclass
class Variant2Wrapper(DataClassORJSONMixin):
    x: Annotated[Variant2, Discriminator(field="type", include_subtypes=True)]

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]


@dataclass
class _Variant2Wrapper:
    x: Annotated[_Variant2, Discriminator(field="type", include_subtypes=True)]

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]


@dataclass
class Variant3(DataClassORJSONMixin):
    x: date
    y: Dict[str, int]

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]
        dialect = DefaultDialect


@dataclass
class _Variant3:
    x: date
    y: Dict[str, int]

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]
        dialect = DefaultDialect


@dataclass
class Variant3Subtype(Variant3):
    type: Literal[3] = 3


@dataclass
class _Variant3Subtype(_Variant3):
    type: Literal[3] = 3


@dataclass
class Variant4(DataClassORJSONMixin):
    x: date
    y: Dict[str, int]

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]
        dialect = DefaultDialect


@dataclass
class _Variant4:
    x: date
    y: Dict[str, int]

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]
        dialect = DefaultDialect


@dataclass
class Variant4Subtype(Variant4):
    type: Literal[4] = 4


@dataclass
class _Variant4Subtype(_Variant4):
    type: Literal[4] = 4


@dataclass
class Variant34Wrapper(DataClassORJSONMixin):
    x: Annotated[
        Union[Variant3, Variant4],
        Discriminator(field="type", include_subtypes=True),
    ]

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]


@dataclass
class _Variant34Wrapper:
    x: Annotated[
        Union[_Variant3, _Variant4],
        Discriminator(field="type", include_subtypes=True),
    ]

    class Config(BaseConfig):
        code_generation_options = [ADD_DIALECT_SUPPORT]


def test_passing_dialect_to_config_based_variant_subtypes():
    assert Variant1.from_dict(
        {"type": 1, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}
    ) == Variant1Subtype1(date(2023, 6, 3), {"1": 2, "3": 4})
    decoder1 = BasicDecoder(_Variant1, default_dialect=DefaultDialect)
    assert decoder1.decode(
        {"type": 1, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}
    ) == _Variant1Subtype1(date(2023, 6, 3), {"1": 2, "3": 4})

    assert Variant1.from_json(
        '{"type": 1, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}'
    ) == Variant1Subtype1(date(2023, 6, 3), {"1": 2, "3": 4})
    decoder2 = ORJSONDecoder(_Variant1, default_dialect=DefaultDialect)
    assert decoder2.decode(
        '{"type": 1, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}'
    ) == _Variant1Subtype1(date(2023, 6, 3), {"1": 2, "3": 4})

    assert Variant1.from_dict(
        {"type": 1, "x": 738674, "y": {"1": 2, "3": 4}}, dialect=MyDialect
    ) == Variant1Subtype1(date(2023, 6, 3), {"1": 2, "3": 4})
    decoder3 = BasicDecoder(_Variant1, default_dialect=MyDialect)
    assert decoder3.decode(
        {"type": 1, "x": 738674, "y": {"1": 2, "3": 4}}
    ) == _Variant1Subtype1(date(2023, 6, 3), {"1": 2, "3": 4})

    assert Variant1.from_json(
        '{"type": 1, "x": 738674, "y": {"1": 2, "3": 4}}', dialect=MyDialect
    ) == Variant1Subtype1(date(2023, 6, 3), {"1": 2, "3": 4})
    decoder4 = ORJSONDecoder(_Variant1, default_dialect=MyDialect)
    assert decoder4.decode(
        '{"type": 1, "x": 738674, "y": {"1": 2, "3": 4}}'
    ) == _Variant1Subtype1(date(2023, 6, 3), {"1": 2, "3": 4})

    @dataclass
    class Variant1Subtype2(Variant1):
        type: Literal[2] = 2

    @dataclass
    class _Variant1Subtype2(_Variant1):
        type: Literal[2] = 2

    assert Variant1.from_dict(
        {"type": 2, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}
    ) == Variant1Subtype2(date(2023, 6, 3), {"1": 2, "3": 4})
    assert decoder1.decode(
        {"type": 2, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}
    ) == _Variant1Subtype2(date(2023, 6, 3), {"1": 2, "3": 4})

    assert Variant1.from_json(
        '{"type": 2, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}'
    ) == Variant1Subtype2(date(2023, 6, 3), {"1": 2, "3": 4})
    assert decoder2.decode(
        '{"type": 2, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}'
    ) == _Variant1Subtype2(date(2023, 6, 3), {"1": 2, "3": 4})

    assert Variant1.from_dict(
        {"type": 2, "x": 738674, "y": {"1": 2, "3": 4}}, dialect=MyDialect
    ) == Variant1Subtype2(date(2023, 6, 3), {"1": 2, "3": 4})
    assert decoder3.decode(
        {"type": 2, "x": 738674, "y": {"1": 2, "3": 4}}
    ) == _Variant1Subtype2(date(2023, 6, 3), {"1": 2, "3": 4})

    assert Variant1.from_json(
        '{"type": 2, "x": 738674, "y": {"1": 2, "3": 4}}', dialect=MyDialect
    ) == Variant1Subtype2(date(2023, 6, 3), {"1": 2, "3": 4})
    assert decoder4.decode(
        '{"type": 2, "x": 738674, "y": {"1": 2, "3": 4}}'
    ) == _Variant1Subtype2(date(2023, 6, 3), {"1": 2, "3": 4})


def test_passing_dialect_to_annotation_based_variant_subtypes():
    assert Variant2Wrapper.from_dict(
        {"x": {"type": 1, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}
    ) == Variant2Wrapper(Variant2Subtype1(date(2023, 6, 3), {"1": 2, "3": 4}))
    decoder1 = BasicDecoder(_Variant2Wrapper)
    assert decoder1.decode(
        {"x": {"type": 1, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}
    ) == _Variant2Wrapper(
        _Variant2Subtype1(date(2023, 6, 3), {"1": 2, "3": 4})
    )

    assert Variant2Wrapper.from_json(
        '{"x": {"type": 1, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}'
    ) == Variant2Wrapper(Variant2Subtype1(date(2023, 6, 3), {"1": 2, "3": 4}))
    decoder2 = ORJSONDecoder(_Variant2Wrapper)
    assert decoder2.decode(
        '{"x": {"type": 1, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}'
    ) == _Variant2Wrapper(
        _Variant2Subtype1(date(2023, 6, 3), {"1": 2, "3": 4})
    )

    assert Variant2Wrapper.from_dict(
        {"x": {"type": 1, "x": 738674, "y": {"1": 2, "3": 4}}},
        dialect=MyDialect,
    ) == Variant2Wrapper(Variant2Subtype1(date(2023, 6, 3), {"1": 2, "3": 4}))
    # "decode" doesn't accept a dialect, so we can't pass MyDialect into it

    assert Variant2Wrapper.from_json(
        '{"x": {"type": 1, "x": 738674, "y": {"1": 2, "3": 4}}}',
        dialect=MyDialect,
    ) == Variant2Wrapper(Variant2Subtype1(date(2023, 6, 3), {"1": 2, "3": 4}))
    # "decode" doesn't accept a dialect, so we can't pass MyDialect into it

    @dataclass
    class Variant2Subtype2(Variant2):
        type: Literal[2] = 2

    @dataclass
    class _Variant2Subtype2(_Variant2):
        type: Literal[2] = 2

    assert Variant2Wrapper.from_dict(
        {"x": {"type": 2, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}
    ) == Variant2Wrapper(Variant2Subtype2(date(2023, 6, 3), {"1": 2, "3": 4}))
    assert decoder1.decode(
        {"x": {"type": 2, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}
    ) == _Variant2Wrapper(
        _Variant2Subtype2(date(2023, 6, 3), {"1": 2, "3": 4})
    )

    assert Variant2Wrapper.from_json(
        '{"x": {"type": 2, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}'
    ) == Variant2Wrapper(Variant2Subtype2(date(2023, 6, 3), {"1": 2, "3": 4}))
    assert decoder2.decode(
        '{"x": {"type": 2, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}'
    ) == _Variant2Wrapper(
        _Variant2Subtype2(date(2023, 6, 3), {"1": 2, "3": 4})
    )

    assert Variant2Wrapper.from_dict(
        {"x": {"type": 2, "x": 738674, "y": {"1": 2, "3": 4}}},
        dialect=MyDialect,
    ) == Variant2Wrapper(Variant2Subtype2(date(2023, 6, 3), {"1": 2, "3": 4}))
    # "decode" doesn't accept a dialect, so we can't pass MyDialect into it

    assert Variant2Wrapper.from_json(
        '{"x": {"type": 2, "x": 738674, "y": {"1": 2, "3": 4}}}',
        dialect=MyDialect,
    ) == Variant2Wrapper(Variant2Subtype2(date(2023, 6, 3), {"1": 2, "3": 4}))
    # "decode" doesn't accept a dialect, so we can't pass MyDialect into it


def test_passing_dialect_to_annotation_based_union_subtypes():
    assert Variant34Wrapper.from_dict(
        {"x": {"type": 3, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}
    ) == Variant34Wrapper(Variant3Subtype(date(2023, 6, 3), {"1": 2, "3": 4}))
    decoder1 = BasicDecoder(_Variant34Wrapper)
    assert decoder1.decode(
        {"x": {"type": 3, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}
    ) == _Variant34Wrapper(
        _Variant3Subtype(date(2023, 6, 3), {"1": 2, "3": 4})
    )

    assert Variant34Wrapper.from_dict(
        {"x": {"type": 4, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}
    ) == Variant34Wrapper(Variant4Subtype(date(2023, 6, 3), {"1": 2, "3": 4}))
    assert decoder1.decode(
        {"x": {"type": 4, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}
    ) == _Variant34Wrapper(
        _Variant4Subtype(date(2023, 6, 3), {"1": 2, "3": 4})
    )

    assert Variant34Wrapper.from_json(
        '{"x": {"type": 3, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}'
    ) == Variant34Wrapper(Variant3Subtype(date(2023, 6, 3), {"1": 2, "3": 4}))
    decoder2 = ORJSONDecoder(_Variant34Wrapper)
    assert decoder2.decode(
        '{"x": {"type": 3, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}'
    ) == _Variant34Wrapper(
        _Variant3Subtype(date(2023, 6, 3), {"1": 2, "3": 4})
    )

    assert Variant34Wrapper.from_json(
        '{"x": {"type": 4, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}'
    ) == Variant34Wrapper(Variant4Subtype(date(2023, 6, 3), {"1": 2, "3": 4}))
    assert decoder2.decode(
        '{"x": {"type": 4, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}'
    ) == _Variant34Wrapper(
        _Variant4Subtype(date(2023, 6, 3), {"1": 2, "3": 4})
    )

    assert Variant34Wrapper.from_dict(
        {"x": {"type": 3, "x": 738674, "y": {"1": 2, "3": 4}}},
        dialect=MyDialect,
    ) == Variant34Wrapper(Variant3Subtype(date(2023, 6, 3), {"1": 2, "3": 4}))
    # "decode" doesn't accept a dialect, so we can't pass MyDialect into it

    assert Variant34Wrapper.from_dict(
        {"x": {"type": 4, "x": 738674, "y": {"1": 2, "3": 4}}},
        dialect=MyDialect,
    ) == Variant34Wrapper(Variant4Subtype(date(2023, 6, 3), {"1": 2, "3": 4}))
    # "decode" doesn't accept a dialect, so we can't pass MyDialect into it

    assert Variant34Wrapper.from_json(
        '{"x": {"type": 3, "x": 738674, "y": {"1": 2, "3": 4}}}',
        dialect=MyDialect,
    ) == Variant34Wrapper(Variant3Subtype(date(2023, 6, 3), {"1": 2, "3": 4}))
    # "decode" doesn't accept a dialect, so we can't pass MyDialect into it

    assert Variant34Wrapper.from_json(
        '{"x": {"type": 4, "x": 738674, "y": {"1": 2, "3": 4}}}',
        dialect=MyDialect,
    ) == Variant34Wrapper(Variant4Subtype(date(2023, 6, 3), {"1": 2, "3": 4}))
    # "decode" doesn't accept a dialect, so we can't pass MyDialect into it

    @dataclass
    class Variant3Subtype2(Variant3):
        type: Literal[5] = 5

    @dataclass
    class _Variant3Subtype2(_Variant3):
        type: Literal[5] = 5

    @dataclass
    class Variant4Subtype2(Variant4):
        type: Literal[6] = 6

    @dataclass
    class _Variant4Subtype2(_Variant4):
        type: Literal[6] = 6

    assert Variant34Wrapper.from_dict(
        {"x": {"type": 5, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}
    ) == Variant34Wrapper(Variant3Subtype2(date(2023, 6, 3), {"1": 2, "3": 4}))
    assert decoder1.decode(
        {"x": {"type": 5, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}
    ) == _Variant34Wrapper(
        _Variant3Subtype2(date(2023, 6, 3), {"1": 2, "3": 4})
    )

    assert Variant34Wrapper.from_dict(
        {"x": {"type": 6, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}
    ) == Variant34Wrapper(Variant4Subtype2(date(2023, 6, 3), {"1": 2, "3": 4}))
    assert decoder1.decode(
        {"x": {"type": 6, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}
    ) == _Variant34Wrapper(
        _Variant4Subtype2(date(2023, 6, 3), {"1": 2, "3": 4})
    )

    assert Variant34Wrapper.from_json(
        '{"x": {"type": 5, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}'
    ) == Variant34Wrapper(Variant3Subtype2(date(2023, 6, 3), {"1": 2, "3": 4}))
    assert decoder2.decode(
        '{"x": {"type": 5, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}'
    ) == _Variant34Wrapper(
        _Variant3Subtype2(date(2023, 6, 3), {"1": 2, "3": 4})
    )

    assert Variant34Wrapper.from_json(
        '{"x": {"type": 6, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}'
    ) == Variant34Wrapper(Variant4Subtype2(date(2023, 6, 3), {"1": 2, "3": 4}))
    assert decoder2.decode(
        '{"x": {"type": 6, "x": "2023-06-03", "y": [["1", 2], ["3", 4]]}}'
    ) == _Variant34Wrapper(
        _Variant4Subtype2(date(2023, 6, 3), {"1": 2, "3": 4})
    )

    assert Variant34Wrapper.from_dict(
        {"x": {"type": 5, "x": 738674, "y": {"1": 2, "3": 4}}},
        dialect=MyDialect,
    ) == Variant34Wrapper(Variant3Subtype2(date(2023, 6, 3), {"1": 2, "3": 4}))
    # "decode" doesn't accept a dialect, so we can't pass MyDialect into it

    assert Variant34Wrapper.from_dict(
        {"x": {"type": 6, "x": 738674, "y": {"1": 2, "3": 4}}},
        dialect=MyDialect,
    ) == Variant34Wrapper(Variant4Subtype2(date(2023, 6, 3), {"1": 2, "3": 4}))
    # "decode" doesn't accept a dialect, so we can't pass MyDialect into it

    assert Variant34Wrapper.from_json(
        '{"x": {"type": 5, "x": 738674, "y": {"1": 2, "3": 4}}}',
        dialect=MyDialect,
    ) == Variant34Wrapper(Variant3Subtype2(date(2023, 6, 3), {"1": 2, "3": 4}))
    # "decode" doesn't accept a dialect, so we can't pass MyDialect into it

    assert Variant34Wrapper.from_json(
        '{"x": {"type": 6, "x": 738674, "y": {"1": 2, "3": 4}}}',
        dialect=MyDialect,
    ) == Variant34Wrapper(Variant4Subtype2(date(2023, 6, 3), {"1": 2, "3": 4}))
    # "decode" doesn't accept a dialect, so we can't pass MyDialect into it
