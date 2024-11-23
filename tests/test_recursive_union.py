from dataclasses import dataclass

from mashumaro import DataClassDictMixin
from mashumaro.codecs import BasicDecoder, BasicEncoder

type JSON = str | int | float | bool | dict[str, JSON] | list[JSON] | None


@dataclass
class MyClass:
    x: str
    y: JSON


def test_encoder_with_recursive_union():
    encoder = BasicEncoder(JSON)
    assert encoder.encode(
        {"x": [{"x": {"x": [{"x": ["x", 1, 1.0, True, None]}]}}]}
    ) == {"x": [{"x": {"x": [{"x": ["x", 1, 1.0, True, None]}]}}]}


def test_encoder_with_recursive_union_in_dataclass():
    encoder = BasicEncoder(MyClass)
    assert encoder.encode(
        MyClass(
            x="x", y={"x": [{"x": {"x": [{"x": ["x", 1, 1.0, True, None]}]}}]}
        )
    ) == {
        "x": "x",
        "y": {"x": [{"x": {"x": [{"x": ["x", 1, 1.0, True, None]}]}}]},
    }


def test_decoder_with_recursive_union():
    decoder = BasicDecoder(JSON)
    assert decoder.decode(
        {"x": [{"x": {"x": [{"x": ["x", 1, 1.0, True, None]}]}}]}
    ) == {"x": [{"x": {"x": [{"x": ["x", 1, 1.0, True, None]}]}}]}


def test_decoder_with_recursive_union_in_dataclass():
    decoder = BasicDecoder(MyClass)
    assert decoder.decode(
        {
            "x": "x",
            "y": {"x": [{"x": {"x": [{"x": ["x", 1, 1.0, True, None]}]}}]},
        }
    ) == MyClass(
        x="x", y={"x": [{"x": {"x": [{"x": ["x", 1, 1.0, True, None]}]}}]}
    )


def test_dataclass_dict_mixin_with_recursive_union():
    @dataclass
    class MyClassWithMixin(DataClassDictMixin):
        x: str
        y: JSON

    assert MyClassWithMixin(
        x="x", y={"x": [{"x": {"x": [{"x": ["x", 1, 1.0, True, None]}]}}]}
    ).to_dict() == {
        "x": "x",
        "y": {"x": [{"x": {"x": [{"x": ["x", 1, 1.0, True, None]}]}}]},
    }
    assert MyClassWithMixin.from_dict(
        {
            "x": "x",
            "y": {"x": [{"x": {"x": [{"x": ["x", 1, 1.0, True, None]}]}}]},
        }
    ) == MyClassWithMixin(
        x="x", y={"x": [{"x": {"x": [{"x": ["x", 1, 1.0, True, None]}]}}]}
    )
